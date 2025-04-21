import uuid
from pathlib import Path
from file_reader import extract_text_from_file
from chunker import chunk_document

import chromadb

from sentence_transformers import SentenceTransformer

# Load local model
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings(texts: list[str]) -> list[list[float]]:
    return model.encode(texts, show_progress_bar=True).tolist()

# =======================================
# 3.3 Storing in ChromaDB (local vector database)
# =======================================

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="dr_x_documents")

# =================================================
# 3.4 Full Pipeline to Store Embeddings with Metadata
# =================================================
def store_document_chunks(filepath: str, chunk_size: int = 500, overlap: int = 50):
    try:
        text = extract_text_from_file(filepath)
        filename = Path(filepath).name
        chunks = chunk_document(text, filename, max_tokens=chunk_size, overlap=overlap)

        if not chunks:
            print(f"⚠️ No chunks generated for {filename}. Skipping.")
            return

        chunk_texts = [chunk['text'] for chunk in chunks]

        embeddings = get_embeddings(chunk_texts)

        for idx, chunk in enumerate(chunks):
            page = chunk['page_number'] if chunk['page_number'] is not None else -1

            collection.add(
                documents=[chunk['text']],
                embeddings=[embeddings[idx]],
                ids=[str(uuid.uuid4())],
                metadatas=[{
                    "filename": chunk['filename'],
                    "page_number": page,
                    "chunk_number": chunk['chunk_number']
                }]
            )
        print(f"✅ Stored {len(chunks)} chunks from {filename} in vector DB.")

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")


# ======================
# CLI Example Execution
# ======================

if __name__ == "__main__":
    folder_path = "files"  # Change this to your folder path
    folder = Path(folder_path)
    files = list(folder.glob("*"))

    print(f"📂 Found {len(files)} files to process.")
    for file in files:
        store_document_chunks(str(file))
