"""
RAG and Document Ingestion module for GTM Agent.
Provides document parsing and relevant context retrieval.
"""
import os
from typing import List, Optional
import re

def load_document_text(file_bytes: bytes, filename: str) -> str:
    """Extracts raw text from uploaded bytes based on file extension."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in [".md", ".txt", ".markdown"]:
        return file_bytes.decode("utf-8", errors="replace")
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"
    else:
        return file_bytes.decode("utf-8", errors="replace")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """Splits document text into manageable chunks for retrieval."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        cleaned_p = p.strip()
        if not cleaned_p:
            continue
        if len(current_chunk) + len(cleaned_p) < chunk_size:
            current_chunk += ("\n\n" + cleaned_p if current_chunk else cleaned_p)
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = cleaned_p
            
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

class SimpleDocIndex:
    """Lightweight in-memory document retriever that handles fast semantic & keyword lookup."""
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.chunks = chunk_text(raw_text)
        
    def query(self, topic: str, top_k: int = 3) -> str:
        """Retrieves the most relevant chunks matching the query keywords."""
        if not self.chunks:
            return self.raw_text[:2000]
            
        words = set(re.findall(r'\w+', topic.lower()))
        scored_chunks = []
        for c in self.chunks:
            chunk_words = set(re.findall(r'\w+', c.lower()))
            score = len(words.intersection(chunk_words))
            scored_chunks.append((score, c))
            
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [c for score, c in scored_chunks[:top_k]]
        return "\n\n---\n\n".join(top_chunks) if top_chunks else self.raw_text[:2000]
