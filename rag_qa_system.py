from sentence_transformers import SentenceTransformer
import chromadb
import subprocess

from translation_utils import setup_translation, translate_to_arabic

# Load local embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="dr_x_documents")


def retrieve_relevant_chunks(question: str, k: int = 5):
    query_embedding = embedder.encode([question])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    return results["documents"][0], results["metadatas"][0]


def generate_answer_with_ollama(question: str, context: str, model: str = "tinyllama"):
    prompt = f"""
You are an expert AI trained to answer questions about scientific documents.

Context:
{context}

Question:
{question}

Answer:"""

    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        capture_output=True
    )

    return result.stdout.decode("utf-8").strip()


# def answer_question(question: str):
#     chunks, metadata = retrieve_relevant_chunks(question)
#     context = "\n\n".join(chunks)
#     answer = generate_answer_with_ollama(question, context)
#     return answer

def answer_question(question: str):
    # Step 1: retrieve chunks
    chunks, metadata = retrieve_relevant_chunks(question)
    context = "\n\n".join(chunks)

    # Step 2: generate English answer
    english_answer = generate_answer_with_ollama(question, context)

    # Step 3: translate to Arabic
    try:
        arabic_answer = translate_to_arabic(english_answer)
    except Exception as e:
        arabic_answer = "⚠️ Translation failed: " + str(e)

    return english_answer, arabic_answer


# if __name__ == "__main__":
#     while True:
#             user_q = input("\n❓ Ask a question about Dr. X's documents (or type 'exit'): ")
#             if user_q.lower() in ['exit', 'quit']:
#                 break
#             response = answer_question(user_q)
#             print("\n💬 Answer:\n", response)

if __name__ == "__main__":
    setup_translation()  # Run once to ensure translation model is installed

    while True:
        user_q = input("\n❓ Ask a question (or type 'exit'): ")
        if user_q.lower() in ['exit', 'quit']:
            break

        english_ans, arabic_ans = answer_question(user_q)

        print("\n💬 English Answer:\n", english_ans)
        print("\n🗣️ Arabic Translation:\n", arabic_ans)