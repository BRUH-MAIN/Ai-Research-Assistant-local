#!/usr/bin/env python3
"""
Simple test server for paper search functionality
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import required modules
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Import our services
from app.services.arxiv_service import ArxivService

# Create FastAPI app
app = FastAPI(title="Paper Search API", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class PaperSearchRequest(BaseModel):
    name: Optional[str] = None
    tags: Optional[List[str]] = None

class PaperSearchResult(BaseModel):
    found_in_db: bool = False
    papers: List[dict] = []
    arxiv_results: Optional[List[dict]] = None

class ArxivPaperDownload(BaseModel):
    arxiv_id: str
    add_tags: Optional[List[str]] = None

# Routes
@app.get("/")
def read_root():
    return {"message": "Paper Search API is running!", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/papers/search")
def search_papers(search_request: PaperSearchRequest):
    """Search for papers (ArXiv only for this simplified version)"""
    try:
        # For this simplified version, we'll only search ArXiv
        if not search_request.name:
            raise HTTPException(status_code=400, detail="Name/query is required")
        
        # Search ArXiv
        arxiv_query = search_request.name
        if search_request.tags:
            # Map common tags to ArXiv categories
            arxiv_cats = []
            for tag in search_request.tags:
                if tag.lower() in ['ai', 'artificial intelligence']:
                    arxiv_cats.append('cs.AI')
                elif tag.lower() in ['ml', 'machine learning']:
                    arxiv_cats.append('cs.LG')
                elif tag.lower() in ['nlp', 'natural language processing']:
                    arxiv_cats.append('cs.CL')
                elif tag.lower() in ['cv', 'computer vision']:
                    arxiv_cats.append('cs.CV')
                elif tag.lower() in ['physics']:
                    arxiv_cats.append('physics')
                else:
                    arxiv_cats.append(tag)
            
            if arxiv_cats:
                arxiv_results = ArxivService.search_by_title_and_tags(
                    search_request.name, arxiv_cats
                )
            else:
                arxiv_results = ArxivService.search_papers(arxiv_query)
        else:
            arxiv_results = ArxivService.search_papers(arxiv_query)
        
        return PaperSearchResult(
            found_in_db=False,
            papers=[],
            arxiv_results=arxiv_results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/v1/papers/download-from-arxiv")
def download_paper_from_arxiv(download_request: ArxivPaperDownload):
    """Download a paper from ArXiv"""
    try:
        # Get paper metadata
        paper_info = ArxivService.get_paper_by_id(download_request.arxiv_id)
        if not paper_info:
            raise HTTPException(status_code=404, detail="Paper not found on ArXiv")
        
        # Download the PDF
        file_path = ArxivService.download_paper(download_request.arxiv_id)
        
        # Return paper info with download confirmation
        return {
            "message": f"Paper downloaded successfully to {file_path}",
            "paper": paper_info,
            "file_path": file_path,
            "added_tags": download_request.add_tags or []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Paper Search API...")
    print("📄 This is a simplified version for testing")
    print("🌐 Access the API at: http://localhost:8000")
    print("📖 View docs at: http://localhost:8000/docs")
    print("🔍 Test search at: http://localhost:8000/api/v1/papers/search")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
