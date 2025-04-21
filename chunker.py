import tiktoken
import re
from pathlib import Path
from typing import List, Dict

# Tokenizer setup
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

def split_text_into_chunks(text: str, max_tokens: int = 500, overlap: int = 50):
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk = tokens[start:end]
        chunks.append(tokenizer.decode(chunk))
        start += max_tokens - overlap
    return chunks

def extract_page_number(chunk_text: str):
    match = re.search(r"\[Page (\d+)]", chunk_text)
    return int(match.group(1)) if match else None

def chunk_document(text: str, filename: str, max_tokens: int = 500, overlap: int = 50) -> List[Dict]:
    raw_chunks = split_text_into_chunks(text, max_tokens=max_tokens, overlap=overlap)
    chunk_data = []
    for idx, chunk in enumerate(raw_chunks):
        page_number = extract_page_number(chunk)
        chunk_data.append({
            "filename": filename,
            "page_number": page_number,
            "chunk_number": idx + 1,
            "text": chunk
        })
    return chunk_data

from file_reader import extract_text_from_file
from chunker import chunk_document

if __name__ == "__main__":
    filepath = "files/OSOS AI Technical Test.pdf"
    text = extract_text_from_file(filepath)
    chunks = chunk_document(text, filename=Path(filepath).name)

    for c in chunks[:2]:  # Print first two chunks
        print(f"\n📄 File: {c['filename']} | 📄 Page: {c['page_number']} | 🔢 Chunk: {c['chunk_number']}")
        print(c["text"][:300])
