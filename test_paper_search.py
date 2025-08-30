#!/usr/bin/env python3
"""
Test script for the paper search functionality
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the backend app to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.arxiv_service import ArxivService

async def test_arxiv_service():
    """Test the ArXiv service functionality"""
    print("Testing ArXiv Service...")
    
    try:
        # Test 1: Basic search
        print("\n1. Testing basic search...")
        papers = ArxivService.search_papers("machine learning", max_results=3)
        print(f"Found {len(papers)} papers")
        for i, paper in enumerate(papers[:2]):
            print(f"  Paper {i+1}: {paper['title'][:80]}...")
        
        # Test 2: Search by title and tags
        print("\n2. Testing search by title and tags...")
        papers = ArxivService.search_by_title_and_tags("attention", ["cs.AI", "cs.LG"], max_results=2)
        print(f"Found {len(papers)} papers with 'attention' in AI/ML categories")
        for i, paper in enumerate(papers):
            print(f"  Paper {i+1}: {paper['title'][:80]}...")
        
        # Test 3: Get specific paper by ID
        print("\n3. Testing get paper by ID...")
        if papers:
            arxiv_id = papers[0]['arxiv_id']
            paper = ArxivService.get_paper_by_id(arxiv_id)
            if paper:
                print(f"  Retrieved paper: {paper['title'][:80]}...")
            else:
                print("  Failed to retrieve paper")
        
        print("\n✅ ArXiv service tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing ArXiv service: {e}")

def test_data_directory():
    """Test that data directory exists and is writable"""
    print("\nTesting data directory...")
    
    data_dir = Path("/home/bharath/Documents/DBMS/data")
    
    if not data_dir.exists():
        print(f"❌ Data directory does not exist: {data_dir}")
        return False
    
    # Test write permission
    test_file = data_dir / "test_write.txt"
    try:
        test_file.write_text("test")
        test_file.unlink()
        print(f"✅ Data directory is writable: {data_dir}")
        return True
    except Exception as e:
        print(f"❌ Data directory is not writable: {e}")
        return False

if __name__ == "__main__":
    print("Starting paper search functionality tests...\n")
    
    # Test data directory
    test_data_directory()
    
    # Test ArXiv service
    asyncio.run(test_arxiv_service())
    
    print("\n🎉 All tests completed!")
