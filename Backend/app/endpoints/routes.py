from flask import Flask, jsonify, request
from urllib.parse import urlparse
import httpx
import uuid
import os

# Langchain Imports
from langchain.llms import OpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Local Imports
from functions.scrape_sitemap import scrape_sitemap
from functions.load_urls import load_urls
from functions.db import initialize_db, store_api_key, get_file_path

# Flask app initialization
app = Flask(__name__)

# Embedding model and database initialization
embedding = OpenAIEmbeddings()
initialize_db()

# Ensure the Pickle_Files directory exists
os.makedirs('./Pickle_Files', exist_ok=True)

# Process Sitemap Endpoint
@app.route('/processSitemap', methods=['POST'])
async def process_sitemap():
    sitemap_url = request.json.get('sitemap_url')
    if not sitemap_url:
        return jsonify({'error': 'Sitemap URL is required'}), 400

    # Validate URL
    parsed_url = urlparse(sitemap_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        return jsonify({'error': 'Invalid domain', 'message': 'The URL provided is not valid.'}), 400

    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(sitemap_url)
            if response.status_code != 200:
                return jsonify({'error': 'Sitemap URL not accessible', 'status_code': response.status_code}), 404
    except httpx.RequestError as e:
        return jsonify({'error': 'Error accessing URL', 'message': str(e)}), 500

    # Scrape sitemap and process data
    xmlurls = await scrape_sitemap(sitemap_url)
    print("Scraped URLs:", xmlurls)

    data = await load_urls(xmlurls)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(data)

    # Create a FAISS vector store
    library = FAISS.from_documents(docs, embedding)
    api_key = "sk-" + str(uuid.uuid4())
    file_path = f"./Pickle_Files/faiss_index_site_content_{api_key}"
    library.save_local(file_path)
    print("Library saved locally")

    # Store the API key and associated file path in the database
    store_api_key(api_key, file_path)

    return jsonify({'status': 'success', 'message': 'Library processed and saved.', 'api_key': api_key})

# Ask Question Endpoint
@app.route('/askQuestion', methods=['POST'])
def ask_question():
    api_key = request.json.get('api_key')
    user_query = request.json.get('query')

    if not api_key or not user_query:
        return jsonify({'error': 'API key and query are required'}), 400

    # Retrieve file path associated with the API key
    file_path = get_file_path(api_key)
    if not file_path:
        return jsonify({'error': 'Invalid API key'}), 404

    try:
        # Load the FAISS index and perform the query
        active_pickle = FAISS.load_local(file_path, embedding, allow_dangerous_deserialization=True)
        qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=active_pickle.as_retriever())
        results = qa.run(user_query)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

if __name__ == "__main__":
    # Run the app on a private IP
    app.run(host="0.0.0.0", port=8000)
