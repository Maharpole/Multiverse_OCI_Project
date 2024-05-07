from flask import Flask, jsonify, request, render_template
from urllib.parse import urlparse
import httpx
import uuid

#langchain imports

from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain_openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter

from functions.scrape_sitemap import scrape_sitemap
from functions.load_urls import load_urls
from functions.db import initialize_db, store_api_key, get_file_path

app = Flask(__name__)
embedding = OpenAIEmbeddings()
initialize_db()

#Front End endpoints

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/question_sandbox', methods=['GET'])
def sandbox():
    return render_template('question_sandbox.html')

#Process Sitemap Endpoint

@app.route('/processSitemap', methods=['POST'])
async def process_sitemap():
    # Retrieve URL from request
    sitemap_url = request.form['sitemap_url']
    print("sitemap_url: ", sitemap_url)
    # Check for valid URL (error handling)
    parsed_url = urlparse(sitemap_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return jsonify(status="Invalid domain", message="The URL provided is not valid."), 400

    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(sitemap_url)
            if response.status_code != 200:
                return jsonify(status="Sitemap URL not accessible", message=f"HTTP status code: {response.status_code}"), 404
    except httpx.RequestError as e:
        return jsonify(status="Error accessing URL", message=str(e)), 500

    # Scrape and retrieve a list of all URLs from all XMLs to retrieve a full list of URLs from a website's sitemap
    xmlurls = await scrape_sitemap(sitemap_url)

    #DEBUG: print the results of scrape_sitemap
    print("xmlurls:", xmlurls)

    # Use Unstructured URL loader to split the contents of each page into documents
    data = await load_urls(xmlurls)
    # Split the documents that were created in the load_urls function into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    docs = text_splitter.split_documents(data)

    # Create a Vector library from the documents
    library = FAISS.from_documents(docs, embedding)

    # Generate an API Key that is associated with this Vector library
    api_key = "sk-" + str(uuid.uuid4())

    # Save library to a .pkl file that can be read again in the future
    file_path = f"./Pickle_Files/faiss_index_site_content_{api_key}"

    library.save_local(file_path)

    print("Library saved Locally")

    # store the api key along with the file path associated
    store_api_key(api_key, file_path)

    # Return a success message with the API key
    return jsonify(status="Success", message="Library processed and saved.", api_key=api_key)

#Ask Question Endpoint

@app.route('/askQuestion', methods=['POST'])
def ask_question():
    # Extract API key and query from the POST request
    api_key = request.json.get('api_key')
    user_query = request.json.get('query')

    if not api_key or not user_query:
        return jsonify({'error': 'Missing API key or query'}), 400

    # Retrieve the associated file path using the API key
    file_path = get_file_path(api_key)
    if not file_path:
        return jsonify({'error': 'Invalid API key'}), 404

    # Load data and perform the query
    active_pickle = FAISS.load_local(file_path, embedding, allow_dangerous_deserialization=True)
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever = active_pickle.as_retriever())
    results = qa.invoke(user_query)
    return jsonify({'results': results})

#TODO: Additional Ideas:
#can pass the raw answers (and potential links that the content was found in) to a low-token, high-performance LLM like GPT 4 to serve a more "human readable" answer that can be fine-tuned with previous support representative data to fit with a companies tone and provide contextual links for where to find the relevant information
# can provide additional links/answers based on a range from the similarity score to better answer a potential client's question.
# error handling for if nothing similar enough is found, can potentially run a "library.similarity_search_with_score(Query)" to determine the relatedness of the answer that can be given, additional logic can be made to reject answers that were not able to find a similar enough answer
#Query_Answer = library.similarity_search(query) will run a similarity search from the vector database to the query
