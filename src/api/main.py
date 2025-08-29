"""
FastAPI application for querying PubMed and retrieving structured information.

This application provides a simple REST API for searching PubMed articles
and retrieving structured data about Thai Traditional Medicine research.
"""

from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
import os

from src.models.source import Source
from src.connectors.pubmed import PubMedConnector
from src.models.pubmed import PubmedArticle
from src.utils.pubmed_query_builder import (
    PubMedQueryBuilder,
    DateRange,
    ArticleType,
    build_thai_traditional_medicine_query
)
from src.utils.rate_limiting import configure_rate_limiting, acquire_rate_limit
from src.api.sanitization import sanitize_text, sanitize_query, sanitize_list
from src.api.monitoring import MonitoringMiddleware, metrics_endpoint
from src.api.security import HTTPSMiddleware
from src.api.audit import AuditLogger

# Import dashboard router
from src.dashboard.router import router as dashboard_router

app = FastAPI(
    title="Thai Traditional Medicine PubMed API",
    description="API for querying PubMed for Thai Traditional Medicine research articles",
    version="0.1.0"
)

# Add HTTPS middleware
app.add_middleware(HTTPSMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Configure rate limiting for the API
# Conservative limits to respect PubMed's API guidelines
configure_rate_limiting("api_search", 1.0, 3.0)  # 1 request/sec, 3 burst
configure_rate_limiting("api_fetch", 1.0, 3.0)   # 1 request/sec, 3 burst

# Create a global source and connector for the application
source = Source(
    id=1,
    name="PubMed",
    type="academic",
    url="https://pubmed.ncbi.nlm.nih.gov/",
    api_endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
    access_method="api",
    reliability_score=5,
    metadata={"api_key": None}
)

connector = PubMedConnector(source)

# Include dashboard router
app.include_router(dashboard_router)

# Serve static files (including the dashboard)
static_dir = os.path.join(os.path.dirname(__file__), "..", "dashboard")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Pydantic models for request/response
class SearchRequest(BaseModel):
    """Request model for searching PubMed articles."""
    query: str
    max_results: Optional[int] = 10
    # Additional search parameters
    include_thai_terms: Optional[bool] = False
    exclude_terms: Optional[List[str]] = []
    article_types: Optional[List[str]] = []
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ArticleResponse(BaseModel):
    """Response model for a PubMed article."""
    pmid: str
    title: Optional[str]
    abstract: Optional[str]
    authors: Optional[List[str]]
    journal: Optional[str]
    publication_date: Optional[str]
    doi: Optional[str]
    language: Optional[str]
    article_type: Optional[str]
    mesh_terms: Optional[List[str]]
    chemicals: Optional[List[str]]
    country: Optional[str]

class SearchResponse(BaseModel):
    """Response model for search results."""
    query: str
    total_results: int
    articles: List[ArticleResponse]

def convert_pubmed_article_to_response(article: PubmedArticle) -> ArticleResponse:
    """Convert a PubmedArticle to an ArticleResponse."""
    return ArticleResponse(
        pmid=article.pmid,
        title=article.title,
        abstract=article.abstract,
        authors=[author.name for author in article.authors] if article.authors else None,
        journal=article.journal.title if article.journal else None,
        publication_date=article.publication_date,
        doi=article.doi,
        language=article.language,
        article_type=article.article_type,
        mesh_terms=article.mesh_terms,
        chemicals=article.chemicals,
        country=article.country
    )

@app.get("/")
async def root():
    """Root endpoint with basic information about the API."""
    return {
        "message": "Thai Traditional Medicine PubMed API",
        "description": "API for querying PubMed for Thai Traditional Medicine research articles",
        "endpoints": {
            "search": "/search",
            "thai_medicine_search": "/thai-medicine-search",
            "health": "/health",
            "metrics": "/metrics",
            "dashboard": "/dashboard"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "thai-traditional-medicine-pubmed-api"
    }

@app.get("/metrics")
async def metrics():
    """Metrics endpoint for Prometheus."""
    return await metrics_endpoint()

@app.get("/search", response_model=SearchResponse)
async def search_pubmed(
    request: Request,
    query: str = Query(..., description="Search query"),
    max_results: int = Query(10, description="Maximum number of results to return", le=100),
    include_thai_terms: bool = Query(False, description="Include Thai-specific terms in search"),
    exclude_terms: List[str] = Query([], description="Terms to exclude from search"),
    article_types: List[str] = Query([], description="Article types to filter by"),
    start_date: Optional[date] = Query(None, description="Start date for publication date range"),
    end_date: Optional[date] = Query(None, description="End date for publication date range")
):
    """
    Search PubMed for articles based on the provided query and filters.
    """
    # Log the request
    AuditLogger.log_request(request)
    
    # Sanitize inputs
    query = sanitize_query(query)
    exclude_terms = sanitize_list(exclude_terms)
    article_types = sanitize_list(article_types)
    
    # Rate limiting for API endpoint
    if not acquire_rate_limit("api_search", 1.0, timeout=5.0):
        AuditLogger.log_security_event(
            event_type="rate_limit_exceeded",
            description="Rate limit exceeded for search endpoint",
            ip_address=request.client.host if request.client else None,
            severity="medium"
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    try:
        # Build the query
        if include_thai_terms or exclude_terms or article_types or (start_date and end_date):
            builder = PubMedQueryBuilder()
            builder.search(query)
            
            if include_thai_terms:
                builder.and_words(["thai", "herbal"])
            
            if exclude_terms:
                builder.not_words(exclude_terms)
            
            if article_types:
                # Convert string article types to ArticleType enums
                for article_type_str in article_types:
                    try:
                        article_type = ArticleType[article_type_str.upper().replace(" ", "_")]
                        builder.article_type(article_type)
                    except KeyError:
                        # If the article type is not recognized, skip it
                        pass
            
            if start_date and end_date:
                date_range = DateRange(start_date, end_date)
                builder.date_range(date_range)
            
            search_query = builder.build()
        else:
            search_query = query
        
        # Search for articles
        pmids = connector.search_articles(search_query, max_results)
        
        # Log data access
        AuditLogger.log_data_access(
            data_type="pubmed_articles",
            action="search",
            ip_address=request.client.host if request.client else None,
            record_count=len(pmids)
        )
        
        if not pmids:
            return SearchResponse(
                query=search_query,
                total_results=0,
                articles=[]
            )
        
        # Fetch article details
        articles = connector.fetch_article_details(pmids)
        
        # Log data access
        AuditLogger.log_data_access(
            data_type="pubmed_articles",
            action="retrieve",
            ip_address=request.client.host if request.client else None,
            record_count=len(articles)
        )
        
        # Convert to response format
        article_responses = [convert_pubmed_article_to_response(article) for article in articles]
        
        return SearchResponse(
            query=search_query,
            total_results=len(article_responses),
            articles=article_responses
        )
        
    except Exception as e:
        AuditLogger.log_security_event(
            event_type="search_error",
            description=f"Error searching PubMed: {str(e)}",
            ip_address=request.client.host if request.client else None,
            severity="high"
        )
        raise HTTPException(status_code=500, detail=f"Error searching PubMed: {str(e)}")

@app.get("/thai-medicine-search", response_model=SearchResponse)
async def search_thai_traditional_medicine(
    request: Request,
    additional_terms: List[str] = Query([], description="Additional terms to include in search"),
    exclude_terms: List[str] = Query([], description="Terms to exclude from search"),
    article_types: List[str] = Query([], description="Article types to filter by"),
    start_date: Optional[date] = Query(None, description="Start date for publication date range"),
    end_date: Optional[date] = Query(None, description="End date for publication date range"),
    max_results: int = Query(10, description="Maximum number of results to return", le=100)
):
    """
    Search PubMed specifically for Thai Traditional Medicine articles using a specialized query.
    """
    # Log the request
    AuditLogger.log_request(request)
    
    # Sanitize inputs
    additional_terms = sanitize_list(additional_terms)
    exclude_terms = sanitize_list(exclude_terms)
    article_types = sanitize_list(article_types)
    
    # Rate limiting for API endpoint
    if not acquire_rate_limit("api_search", 1.0, timeout=5.0):
        AuditLogger.log_security_event(
            event_type="rate_limit_exceeded",
            description="Rate limit exceeded for Thai medicine search endpoint",
            ip_address=request.client.host if request.client else None,
            severity="medium"
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    try:
        # Convert string article types to ArticleType enums
        article_type_enums = []
        for article_type_str in article_types:
            try:
                article_type = ArticleType[article_type_str.upper().replace(" ", "_")]
                article_type_enums.append(article_type)
            except KeyError:
                # If the article type is not recognized, skip it
                pass
        
        # Build the specialized query
        date_range = None
        if start_date and end_date:
            date_range = DateRange(start_date, end_date)
        
        search_query = build_thai_traditional_medicine_query(
            additional_terms=additional_terms if additional_terms else None,
            exclude_terms=exclude_terms if exclude_terms else None,
            date_range=date_range,
            article_types=article_type_enums if article_type_enums else None
        )
        
        # Search for articles
        pmids = connector.search_articles(search_query, max_results)
        
        # Log data access
        AuditLogger.log_data_access(
            data_type="pubmed_articles",
            action="search",
            ip_address=request.client.host if request.client else None,
            record_count=len(pmids)
        )
        
        if not pmids:
            return SearchResponse(
                query=search_query,
                total_results=0,
                articles=[]
            )
        
        # Fetch article details
        articles = connector.fetch_article_details(pmids)
        
        # Log data access
        AuditLogger.log_data_access(
            data_type="pubmed_articles",
            action="retrieve",
            ip_address=request.client.host if request.client else None,
            record_count=len(articles)
        )
        
        # Convert to response format
        article_responses = [convert_pubmed_article_to_response(article) for article in articles]
        
        return SearchResponse(
            query=search_query,
            total_results=len(article_responses),
            articles=article_responses
        )
        
    except Exception as e:
        AuditLogger.log_security_event(
            event_type="search_error",
            description=f"Error searching PubMed: {str(e)}",
            ip_address=request.client.host if request.client else None,
            severity="high"
        )
        raise HTTPException(status_code=500, detail=f"Error searching PubMed: {str(e)}")

@app.get("/article/{pmid}", response_model=ArticleResponse)
async def get_article(request: Request, pmid: str):
    """
    Get detailed information about a specific PubMed article by PMID.
    """
    # Log the request
    AuditLogger.log_request(request)
    
    # Rate limiting for API endpoint
    if not acquire_rate_limit("api_fetch", 1.0, timeout=5.0):
        AuditLogger.log_security_event(
            event_type="rate_limit_exceeded",
            description="Rate limit exceeded for article retrieval endpoint",
            ip_address=request.client.host if request.client else None,
            severity="medium"
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    try:
        articles = connector.fetch_article_details([pmid])
        
        # Log data access
        AuditLogger.log_data_access(
            data_type="pubmed_articles",
            action="retrieve",
            ip_address=request.client.host if request.client else None,
            record_count=len(articles)
        )
        
        if not articles:
            AuditLogger.log_security_event(
                event_type="article_not_found",
                description=f"Article with PMID {pmid} not found",
                ip_address=request.client.host if request.client else None,
                severity="low"
            )
            raise HTTPException(status_code=404, detail=f"Article with PMID {pmid} not found")
        
        return convert_pubmed_article_to_response(articles[0])
        
    except Exception as e:
        AuditLogger.log_security_event(
            event_type="fetch_error",
            description=f"Error fetching article: {str(e)}",
            ip_address=request.client.host if request.client else None,
            severity="high"
        )
        raise HTTPException(status_code=500, detail=f"Error fetching article: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)