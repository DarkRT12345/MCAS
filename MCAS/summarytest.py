from flask import Flask, request, render_template
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from language_tool_python import LanguageTool
from youtube_transcript_api import YouTubeTranscriptApi
import json
import sys

tool = LanguageTool('en-US')

def download_youtube_subtitle(video_id, output_file='transcriptofvid.txt', language='en'):
    """
    Download subtitles of the YouTube video with the given video ID and save them to a file.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        subtitle_text = " ".join([entry['text'] for entry in transcript])
        
        # Save transcript to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(subtitle_text)
        
        return subtitle_text
    except Exception as e:
        print(f"An error occurred while downloading subtitles: {e}")
        return None

def chunk_text(text, chunk_size=500):
    """Splits text into smaller chunks of specified size for summarization."""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

def summarize_text(text, max_length=150):
    tokenizer = AutoTokenizer.from_pretrained("C:/Users/User/Desktop/Assignment/New folder/testcorrectmodel", use_fast=False)
    model = AutoModelForSeq2SeqLM.from_pretrained("C:/Users/User/Desktop/Assignment/New folder/testcorrectmodel")
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
    
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def post_process_summary(summary):
    """
    Use LanguageTool to correct grammar and punctuation in the summary.
    """
    corrected_summary = tool.correct(summary)
    return corrected_summary

video_id = sys.argv[1]
transcript = download_youtube_subtitle(video_id)

chunked_summary = []
for chunk in chunk_text(transcript, chunk_size=500):
    chunked_summary.append(summarize_text(chunk))
    
# Combine summaries of each chunk
final_summary = " ".join(chunked_summary)
corrected_summary = post_process_summary(final_summary)

print (corrected_summary)
output_summary_file = 'summary.txt'
with open(output_summary_file, 'w', encoding='utf-8') as file:
    file.write(corrected_summary)