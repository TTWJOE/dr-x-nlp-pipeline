from transformers import pipeline
from file_reader import extract_text_from_file
from chunker import chunk_document, tokenizer
from pathlib import Path
from rouge_score import rouge_scorer
import time

# Load summarization model (lightweight)
summarizer = pipeline("summarization", model="Falconsai/text_summarization")

# Setup ROUGE scorer
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

def summarize_text(text: str, max_input_words: int = 800) -> str:
    words = text.split()
    if len(words) > max_input_words:
        text = " ".join(words[:max_input_words])  # truncate input

    summary = summarizer(text, max_length=1500, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def summarize_file(filepath: str):
    print(f"\n📄 Summarizing: {filepath}")
    filename = Path(filepath).name

    # Step 1: Extract text
    text = extract_text_from_file(filepath)
    if not text.strip():
        print("⚠️ Skipping empty file.")
        return None

    # Step 2: Token count
    token_count = len(tokenizer.encode(text))

    # Step 3: Summarize with timing
    start = time.perf_counter()
    summary = summarize_text(text)
    end = time.perf_counter()
    duration = end - start
    tps = token_count / duration if duration > 0 else 0

    # Step 4: ROUGE Score
    rouge_scores = scorer.score(text, summary)

    # Output
    print("\n📝 Summary:")
    print(summary)

    print(f"\n⏱️ {token_count} tokens in {duration:.2f}s → {tps:.2f} tokens/sec")
    print(f"📊 ROUGE-1: {rouge_scores['rouge1'].fmeasure:.4f} | "
          f"ROUGE-2: {rouge_scores['rouge2'].fmeasure:.4f} | "
          f"ROUGE-L: {rouge_scores['rougeL'].fmeasure:.4f}")

    return summary, rouge_scores

# Run batch summarization
if __name__ == "__main__":
    folder_path = "files"
    folder = Path(folder_path)
    files = list(folder.glob("*"))

    print(f"📂 Found {len(files)} files to process.")
    for file in files:
        summarize_file(str(file))
