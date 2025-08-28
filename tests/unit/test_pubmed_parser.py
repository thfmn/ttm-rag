"""
Unit tests for PubMed XML parsing utilities.

These tests verify that our XML parsing functions correctly convert
PubMed XML data into structured Pydantic models.
"""

import sys
import os
import pytest
from xml.etree import ElementTree as ET

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.pubmed_parser import (
    parse_pubmed_xml, 
    _parse_single_article,
    _parse_authors,
    _parse_journal,
    _parse_doi,
    _parse_mesh_terms,
    _parse_chemicals
)
from tests.fixtures.pubmed_xml_samples import (
    SIMPLE_PUBMED_XML, 
    MINIMAL_PUBMED_XML, 
    INVALID_PMID_XML
)


class TestPubmedParser:
    """Tests for the PubMed XML parser."""
    
    def test_parse_pubmed_xml_simple(self):
        """Test parsing simple PubMed XML."""
        articles = parse_pubmed_xml(SIMPLE_PUBMED_XML)
        
        # Should have one article
        assert len(articles) == 1
        
        article = articles[0]
        
        # Check PMID
        assert article.pmid == "12345678"
        
        # Check title
        assert article.title == "Traditional Medicine in Modern Healthcare"
        
        # Check abstract
        assert article.abstract == "This article discusses the integration of traditional medicine practices into modern healthcare systems."
        
        # Check authors
        assert len(article.authors) == 2
        assert article.authors[0].name == "John A Smith"
        assert article.authors[0].affiliation == "Department of Medicine, University Hospital"
        assert article.authors[1].name == "Sarah B Johnson"
        assert article.authors[1].affiliation == "Institute of Traditional Medicine, University of Health Sciences"
        
        # Check journal
        assert article.journal is not None
        assert article.journal.title == "The New England journal of medicine"
        assert article.journal.issn == "0028-4793"
        assert article.journal.volume == "390"
        assert article.journal.issue == "4"
        
        # Check DOI
        assert article.doi == "10.1056/NEJMra2345678"
        
        # Check language
        assert article.language == "eng"
        
        # Check country
        assert article.country == "United States"
        
        # Check article type
        assert article.article_type == "Journal Article"
        
        # Check MeSH terms
        assert "Plant Extracts" in article.mesh_terms
        assert "Analgesics" in article.mesh_terms
        assert "Medicine, Traditional" in article.mesh_terms
        
        # Check chemicals
        assert "Plant Extracts" in article.chemicals
        assert "Analgesics" in article.chemicals
        
        # Check raw XML is preserved
        assert article.raw_xml == SIMPLE_PUBMED_XML
    
    def test_parse_pubmed_xml_minimal(self):
        """Test parsing minimal PubMed XML."""
        articles = parse_pubmed_xml(MINIMAL_PUBMED_XML)
        
        # Should have one article
        assert len(articles) == 1
        
        article = articles[0]
        
        # Check PMID
        assert article.pmid == "87654321"
        
        # Check title
        assert article.title == "Research on Medical Treatments"
        
        # Check that optional fields are None or empty
        assert article.abstract is None
        assert article.authors == []
        assert article.journal is not None
        assert article.journal.title == "Journal of Medical Research"
        assert article.doi is None
    
    def test_parse_pubmed_xml_invalid_pmid(self):
        """Test parsing XML with invalid PMID."""
        # The parser should log the error but continue processing
        # Since there's only one article with invalid PMID, result should be empty
        articles = parse_pubmed_xml(INVALID_PMID_XML)
        assert articles == []  # Should return empty list when all articles fail validation
    
    def test_parse_pubmed_xml_malformed(self):
        """Test parsing malformed XML."""
        with pytest.raises(ET.ParseError):
            parse_pubmed_xml("This is not XML")
    
    def test_parse_pubmed_xml_empty(self):
        """Test parsing empty XML."""
        articles = parse_pubmed_xml("<?xml version='1.0'?><PubmedArticleSet></PubmedArticleSet>")
        assert articles == []
    
    def test_parse_single_article_missing_pmid(self):
        """Test parsing article with missing PMID."""
        # Create XML with missing PMID
        xml_without_pmid = '''<?xml version="1.0"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <Article>
                        <ArticleTitle>Test Article</ArticleTitle>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>'''
        
        root = ET.fromstring(xml_without_pmid)
        article_element = root.find('.//PubmedArticle')
        
        # This should raise a ValueError
        with pytest.raises(ValueError, match="Missing PMID in article"):
            _parse_single_article(article_element, xml_without_pmid)


class TestParseAuthors:
    """Tests for the _parse_authors function."""
    
    def test_parse_authors_simple(self):
        """Test parsing authors from XML."""
        root = ET.fromstring(SIMPLE_PUBMED_XML)
        article_element = root.find('.//PubmedArticle')
        
        authors = _parse_authors(article_element)
        
        assert len(authors) == 2
        assert authors[0].name == "John A Smith"
        assert authors[0].affiliation == "Department of Medicine, University Hospital"
        assert authors[1].name == "Sarah B Johnson"
        assert authors[1].affiliation == "Institute of Traditional Medicine, University of Health Sciences"


class TestParseJournal:
    """Tests for the _parse_journal function."""
    
    def test_parse_journal_simple(self):
        """Test parsing journal from XML."""
        root = ET.fromstring(SIMPLE_PUBMED_XML)
        article_element = root.find('.//PubmedArticle')
        
        journal = _parse_journal(article_element)
        
        assert journal is not None
        assert journal.title == "The New England journal of medicine"
        assert journal.issn == "0028-4793"
        assert journal.volume == "390"
        assert journal.issue == "4"


class TestParseDOI:
    """Tests for the _parse_doi function."""
    
    def test_parse_doi_simple(self):
        """Test parsing DOI from XML."""
        root = ET.fromstring(SIMPLE_PUBMED_XML)
        article_element = root.find('.//PubmedArticle')
        
        doi = _parse_doi(article_element)
        
        assert doi == "10.1056/NEJMra2345678"


class TestParseMeshTerms:
    """Tests for the _parse_mesh_terms function."""
    
    def test_parse_mesh_terms_simple(self):
        """Test parsing MeSH terms from XML."""
        root = ET.fromstring(SIMPLE_PUBMED_XML)
        article_element = root.find('.//PubmedArticle')
        
        mesh_terms = _parse_mesh_terms(article_element)
        
        assert "Plant Extracts" in mesh_terms
        assert "Analgesics" in mesh_terms
        assert "Medicine, Traditional" in mesh_terms
        assert len(mesh_terms) == 3


class TestParseChemicals:
    """Tests for the _parse_chemicals function."""
    
    def test_parse_chemicals_simple(self):
        """Test parsing chemicals from XML."""
        root = ET.fromstring(SIMPLE_PUBMED_XML)
        article_element = root.find('.//PubmedArticle')
        
        chemicals = _parse_chemicals(article_element)
        
        assert "Plant Extracts" in chemicals
        assert "Analgesics" in chemicals
        assert len(chemicals) == 2