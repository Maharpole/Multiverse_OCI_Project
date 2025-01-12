from flask import Flask, jsonify, request, render_template
from urllib.parse import urlparse
import httpx
import uuid
import os

# Langchain Imports
from langchain.indexes.vectorstore import VectorstoreIndexCreator
from langchain_openai import OpenAI
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Local Imports
from functions.scrape_sitemap import scrape_sitemap
from functions.load_urls import load_urls
from functions.db import initialize_db, store_api_key, get_file_path

app = Flask(__name__)

embedding = OpenAIEmbeddings()
initialize_db()

# Ensure the Pickle_Files directory exists
os.makedirs('./Pickle_Files', exist_ok=True)

# Front End Endpoints
@app.route('/', methods=['GET'])
def login():
    return render_template("login.html")

@app.route('/question_sandbox', methods=['GET'])
def sandbox():
    return render_template("question_sandbox.html")

@app.route('/home', methods=['GET'])
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET'])
def register():
    return render_template("register.html")

# Process Sitemap Endpoint
@app.route('/processSitemap', methods=['POST'])
async def process_sitemap():
    sitemap_url = request.form['sitemap_url']
    print("sitemap_url: ", sitemap_url)

    # Validate URL
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

    xmlurls = await scrape_sitemap(sitemap_url)
    print("xmlurls:", xmlurls)

    data = await load_urls(xmlurls)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    docs = text_splitter.split_documents(data)

    library = FAISS.from_documents(docs, embedding)
    api_key = "sk-" + str(uuid.uuid4())
    file_path = f"./Pickle_Files/faiss_index_site_content_{api_key}"
    library.save_local(file_path)
    print("Library saved Locally")

    store_api_key(api_key, file_path)
    return jsonify(status="Success", message="Library processed and saved.", api_key=api_key)

# Ask Question Endpoint
@app.route('/askQuestion', methods=['POST'])
def ask_question():
    api_key = request.form['api_key']
    user_query = request.form['query']

    if not api_key or not user_query:
        return jsonify({'error': 'Missing API key or query'}), 400

    file_path = get_file_path(api_key)
    if not file_path:
        return jsonify({'error': 'Invalid API key'}), 404

    active_pickle = FAISS.load_local(file_path, embedding, allow_dangerous_deserialization=True)
    qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=active_pickle.as_retriever())
    results = qa.invoke(user_query)
    return jsonify({'results': results})
