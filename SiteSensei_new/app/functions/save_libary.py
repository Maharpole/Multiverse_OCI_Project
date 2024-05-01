import faiss

def save_library(index, filename):
    # Extract the FAISS index if possible
    if hasattr(index, 'faiss_index'):
        faiss_index = index.faiss_index  # Hypothetical attribute holding the actual FAISS index
        # Serialize FAISS index using FAISS's native serialization
        faiss.write_index(faiss_index, filename)
    else:
        # Fallback: serialize the entire object using pickle if direct index access isn't available
        with open(filename, 'wb') as f:
            pickle.dump(vector_store, f)

def load_library(filename):
    """Load a FAISS index from a file."""
    try:
        return faiss.read_index(filename)
    except Exception as e:
        print(f"Failed to load the index from {filename}: {e}")
        raise
