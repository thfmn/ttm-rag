"""
Unit tests for PubMed Pydantic models.

These tests verify that our Pydantic models correctly validate
and structure PubMed data according to our requirements.
"""

import sys
import os
import pytest
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.models.pubmed import PubmedAuthor, PubmedJournal, PubmedArticle


class TestPubmedAuthor:
    """Tests for the PubmedAuthor model."""
    
    def test_author_creation_with_all_fields(self):
        """Test creating an author with all fields populated."""
        author = PubmedAuthor(
            name="John Smith",
            affiliation="Department of Medicine, University Hospital",
            orcid="0000-0000-0000-0000"
        )
        
        assert author.name == "John Smith"
        assert author.affiliation == "Department of Medicine, University Hospital"
        assert author.orcid == "0000-0000-0000-0000"
    
    def test_author_creation_with_optional_fields_missing(self):
        """Test creating an author with only required fields."""
        author = PubmedAuthor()
        
        assert author.name is None
        assert author.affiliation is None
        assert author.orcid is None
    
    def test_author_partial_fields(self):
        """Test creating an author with some fields populated."""
        author = PubmedAuthor(
            name="Jane Doe",
            orcid="0000-0000-0000-0001"
        )
        
        assert author.name == "Jane Doe"
        assert author.affiliation is None
        assert author.orcid == "0000-0000-0000-0001"


class TestPubmedJournal:
    """Tests for the PubmedJournal model."""
    
    def test_journal_creation_with_all_fields(self):
        """Test creating a journal with all fields populated."""
        pub_date = datetime(2023, 6, 15)
        journal = PubmedJournal(
            title="Journal of Traditional Medicine",
            issn="1234-5678",
            volume="15",
            issue="3",
            publication_date=pub_date
        )
        
        assert journal.title == "Journal of Traditional Medicine"
        assert journal.issn == "1234-5678"
        assert journal.volume == "15"
        assert journal.issue == "3"
        assert journal.publication_date == pub_date
    
    def test_journal_creation_with_optional_fields_missing(self):
        """Test creating a journal with only required fields."""
        journal = PubmedJournal()
        
        assert journal.title is None
        assert journal.issn is None
        assert journal.volume is None
        assert journal.issue is None
        assert journal.publication_date is None


class TestPubmedArticle:
    """Tests for the PubmedArticle model."""
    
    def test_article_creation_with_required_fields(self):
        """Test creating an article with only required fields."""
        article = PubmedArticle(
            pmid="12345678"
        )
        
        assert article.pmid == "12345678"
        assert article.title is None
        assert article.abstract is None
        assert article.authors == []
        assert article.journal is None
        assert article.publication_date is None
        assert article.article_type is None
        assert article.keywords == []
        assert article.doi is None
        assert article.language == "eng"
        assert article.country is None
        assert article.mesh_terms == []
        assert article.chemicals == []
        assert article.references == []
        assert article.raw_xml is None
    
    def test_article_creation_with_all_fields(self):
        """Test creating an article with all fields populated."""
        # Create author
        author = PubmedAuthor(
            name="John Smith",
            affiliation="Department of Medicine"
        )
        
        # Create journal
        pub_date = datetime(2023, 6, 15)
        journal = PubmedJournal(
            title="Journal of Traditional Medicine",
            issn="1234-5678"
        )
        
        # Create article
        article = PubmedArticle(
            pmid="12345678",
            title="Traditional Medicine in Modern Healthcare",
            abstract="This article discusses the role of traditional medicine...",
            authors=[author],
            journal=journal,
            publication_date=pub_date,
            article_type="Research Article",
            keywords=["traditional medicine", "healthcare", "integration"],
            doi="10.1234/jtm.2023.12345",
            language="eng",
            country="United States",
            mesh_terms=["Medicine, Traditional", "Healthcare"],
            chemicals=["Chemical A", "Chemical B"],
            references=["Ref1", "Ref2"],
            raw_xml="<xml>...</xml>"
        )
        
        # Verify all fields
        assert article.pmid == "12345678"
        assert article.title == "Traditional Medicine in Modern Healthcare"
        assert article.abstract == "This article discusses the role of traditional medicine..."
        assert len(article.authors) == 1
        assert article.authors[0].name == "John Smith"
        assert article.journal.title == "Journal of Traditional Medicine"
        assert article.publication_date == pub_date
        assert article.article_type == "Research Article"
        assert article.keywords == ["traditional medicine", "healthcare", "integration"]
        assert article.doi == "10.1234/jtm.2023.12345"
        assert article.language == "eng"
        assert article.country == "United States"
        assert article.mesh_terms == ["Medicine, Traditional", "Healthcare"]
        assert article.chemicals == ["Chemical A", "Chemical B"]
        assert article.references == ["Ref1", "Ref2"]
        assert article.raw_xml == "<xml>...</xml>"
    
    def test_pmid_validation_valid(self):
        """Test PMID validation with valid input."""
        article = PubmedArticle(pmid="12345678")
        assert article.pmid == "12345678"
    
    def test_pmid_validation_invalid(self):
        """Test PMID validation with invalid input."""
        with pytest.raises(ValueError, match="PMID must be a numeric string"):
            PubmedArticle(pmid="invalid123")
    
    def test_doi_validation_valid(self):
        """Test DOI validation with valid input."""
        article = PubmedArticle(
            pmid="12345678",
            doi="10.1234/journal.article"
        )
        assert article.doi == "10.1234/journal.article"
    
    def test_doi_validation_invalid(self):
        """Test DOI validation with invalid input."""
        with pytest.raises(ValueError, match="DOI should start with \"10.\""):
            PubmedArticle(
                pmid="12345678",
                doi="invalid-doi"
            )
    
    def test_default_language(self):
        """Test that default language is English."""
        article = PubmedArticle(pmid="12345678")
        assert article.language == "eng"