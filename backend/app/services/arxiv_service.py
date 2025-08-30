"""
ArXiv service for searching and downloading papers
"""
import os
import arxiv
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from app.core.config import settings


class ArxivService:
    """Service for interacting with ArXiv API"""
    
    @staticmethod
    def search_papers(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for papers on ArXiv
        
        Args:
            query: Search query (can include title, authors, tags, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of paper metadata dictionaries
        """
        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            for result in client.results(search):
                paper_data = {
                    "title": result.title,
                    "abstract": result.summary,
                    "authors": ", ".join([str(author) for author in result.authors]),
                    "doi": result.doi if result.doi else None,
                    "published_at": result.published.isoformat() if result.published else None,
                    "source_url": result.entry_id,
                    "pdf_url": result.pdf_url,
                    "arxiv_id": result.entry_id.split('/')[-1],
                    "categories": result.categories,
                    "primary_category": result.primary_category
                }
                papers.append(paper_data)
                
            return papers
            
        except Exception as e:
            raise Exception(f"Error searching ArXiv: {str(e)}")
    
    @staticmethod
    def download_paper(arxiv_id: str, filename: Optional[str] = None) -> str:
        """
        Download a paper from ArXiv by its ID
        
        Args:
            arxiv_id: ArXiv paper ID (e.g., "2301.00001")
            filename: Optional custom filename
            
        Returns:
            Path to the downloaded file
        """
        try:
            # Ensure data directory exists
            data_dir = Path(settings.DATA_DIR)
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Get paper info first
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(client.results(search))
            
            # Generate filename if not provided
            if not filename:
                # Clean title for filename
                clean_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_title = clean_title.replace(' ', '_')[:50]  # Limit length
                filename = f"{arxiv_id}_{clean_title}.pdf"
            
            # Download the paper
            filepath = data_dir / filename
            paper.download_pdf(dirpath=str(data_dir), filename=filename)
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Error downloading paper {arxiv_id}: {str(e)}")
    
    @staticmethod
    def get_paper_by_id(arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed paper information by ArXiv ID
        
        Args:
            arxiv_id: ArXiv paper ID
            
        Returns:
            Paper metadata dictionary or None if not found
        """
        try:
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            
            for result in client.results(search):
                return {
                    "title": result.title,
                    "abstract": result.summary,
                    "authors": ", ".join([str(author) for author in result.authors]),
                    "doi": result.doi if result.doi else None,
                    "published_at": result.published.isoformat() if result.published else None,
                    "source_url": result.entry_id,
                    "pdf_url": result.pdf_url,
                    "arxiv_id": result.entry_id.split('/')[-1],
                    "categories": result.categories,
                    "primary_category": result.primary_category
                }
            
            return None
            
        except Exception as e:
            raise Exception(f"Error fetching paper {arxiv_id}: {str(e)}")
    
    @staticmethod
    def search_by_title_and_tags(title: str, tags: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers by title and category tags
        
        Args:
            title: Paper title or keywords
            tags: List of category tags (e.g., ['cs.AI', 'cs.LG'])
            max_results: Maximum number of results
            
        Returns:
            List of matching papers
        """
        try:
            # Build query
            query_parts = []
            
            # Add title search
            if title:
                query_parts.append(f'ti:"{title}"')
            
            # Add category filters
            if tags:
                category_queries = []
                for tag in tags:
                    category_queries.append(f'cat:{tag}')
                if category_queries:
                    query_parts.append(f'({" OR ".join(category_queries)})')
            
            query = " AND ".join(query_parts) if query_parts else title
            
            return ArxivService.search_papers(query, max_results)
            
        except Exception as e:
            raise Exception(f"Error searching by title and tags: {str(e)}")
