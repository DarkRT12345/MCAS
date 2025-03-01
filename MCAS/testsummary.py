from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from language_tool_python import LanguageTool
import sys

# Initialize grammar correction tool
tool = LanguageTool('en-US')

# Load tokenizer and model
model_path = "C:/Users/User/Desktop/Assignment/New folder/testcorrectmodel"
tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

def chunk_text(text, chunk_size=500):
    """Splits text into smaller chunks for summarization."""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

def summarize_text(text, max_length=150):
    """Summarizes the given text."""
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def post_process_summary(summary):
    """Corrects grammar and punctuation in the summary."""
    return tool.correct(summary)

if __name__ == "__main__":
    input_text = sys.stdin.read().strip()
    
    if not input_text:
        print("Error: No input text provided.")
        sys.exit(1)

    # Summarize in chunks
    chunked_summary = [summarize_text(chunk) for chunk in chunk_text(input_text, chunk_size=500)]
    
    # Combine chunks and correct grammar
    final_summary = " ".join(chunked_summary)
    corrected_summary = post_process_summary(final_summary)

    # Print and save summary
    print(corrected_summary)
    
    with open("summary.txt", "w", encoding="utf-8") as file:
        file.write(corrected_summary)
