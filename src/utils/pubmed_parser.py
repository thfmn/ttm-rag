"""
XML parsing utilities for PubMed data.

This module provides functions to parse XML data from the PubMed API
into structured Pydantic models.
"""

from typing import List, Optional
from xml.etree import ElementTree as ET
from src.models.pubmed import PubmedAuthor, PubmedJournal, PubmedArticle
import logging

logger = logging.getLogger(__name__)


def parse_pubmed_xml(xml_content: str) -> List[PubmedArticle]:
    """
    Parse PubMed XML content into a list of PubmedArticle objects.
    
    Args:
        xml_content: XML string from PubMed API
        
    Returns:
        List of PubmedArticle objects
        
    Raises:
        ET.ParseError: If the XML is malformed
        ValueError: If required fields are missing or invalid
    """
    try:
        # Parse the XML
        root = ET.fromstring(xml_content)
        
        # Find all PubmedArticle elements
        articles = root.findall('.//PubmedArticle')
        
        # Parse each article
        parsed_articles = []
        for article_element in articles:
            try:
                parsed_article = _parse_single_article(article_element, xml_content)
                parsed_articles.append(parsed_article)
            except Exception as e:
                logger.warning(f"Failed to parse article: {e}")
                # Continue with other articles even if one fails
                continue
                
        return parsed_articles
        
    except ET.ParseError as e:
        logger.error(f"Failed to parse XML: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing XML: {e}")
        raise


def _parse_single_article(article_element: ET.Element, raw_xml: str) -> PubmedArticle:
    """
    Parse a single PubmedArticle element into a PubmedArticle object.
    
    Args:
        article_element: XML element representing a single article
        raw_xml: The raw XML content (for debugging)
        
    Returns:
        Parsed PubmedArticle object
    """
    # Extract PMID
    pmid_element = article_element.find('.//PMID')
    pmid = pmid_element.text if pmid_element is not None and pmid_element.text else ""
    
    if not pmid:
        raise ValueError("Missing PMID in article")
    
    # Create the basic article object
    article = PubmedArticle(
        pmid=pmid,
        raw_xml=raw_xml
    )
    
    # Extract title
    title_element = article_element.find('.//ArticleTitle')
    if title_element is not None and title_element.text:
        article.title = title_element.text
    
    # Extract abstract
    abstract_element = article_element.find('.//Abstract/AbstractText')
    if abstract_element is not None and abstract_element.text:
        article.abstract = abstract_element.text
    
    # Extract authors
    article.authors = _parse_authors(article_element)
    
    # Extract journal information
    article.journal = _parse_journal(article_element)
    
    # Extract publication date
    article.publication_date = _parse_publication_date(article_element)
    
    # Extract article type
    article.article_type = _parse_article_type(article_element)
    
    # Extract keywords
    article.keywords = _parse_keywords(article_element)
    
    # Extract DOI
    article.doi = _parse_doi(article_element)
    
    # Extract language
    article.language = _parse_language(article_element)
    
    # Extract country
    article.country = _parse_country(article_element)
    
    # Extract MeSH terms
    article.mesh_terms = _parse_mesh_terms(article_element)
    
    # Extract chemicals
    article.chemicals = _parse_chemicals(article_element)
    
    return article


def _parse_authors(article_element: ET.Element) -> List[PubmedAuthor]:
    """
    Parse authors from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        List of PubmedAuthor objects
    """
    authors = []
    author_list = article_element.findall('.//AuthorList/Author')
    
    for author_element in author_list:
        # Extract author name
        last_name = ""
        fore_name = ""
        
        last_name_element = author_element.find('LastName')
        if last_name_element is not None and last_name_element.text:
            last_name = last_name_element.text
        
        fore_name_element = author_element.find('ForeName')
        if fore_name_element is not None and fore_name_element.text:
            fore_name = fore_name_element.text
        
        name = ""
        if fore_name and last_name:
            name = f"{fore_name} {last_name}"
        elif fore_name:
            name = fore_name
        elif last_name:
            name = last_name
        
        # Extract affiliation
        affiliation = ""
        affiliation_element = author_element.find('.//AffiliationInfo/Affiliation')
        if affiliation_element is not None and affiliation_element.text:
            affiliation = affiliation_element.text
        
        # Create author object if we have at least a name
        if name:
            author = PubmedAuthor(
                name=name,
                affiliation=affiliation
            )
            authors.append(author)
    
    return authors


def _parse_journal(article_element: ET.Element) -> Optional[PubmedJournal]:
    """
    Parse journal information from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        PubmedJournal object or None if no journal info
    """
    journal_element = article_element.find('.//Journal')
    if journal_element is None:
        return None
    
    # Extract journal title
    title = ""
    title_element = journal_element.find('Title')
    if title_element is not None and title_element.text:
        title = title_element.text
    
    # Extract ISSN
    issn = ""
    issn_element = journal_element.find('ISSN')
    if issn_element is not None and issn_element.text:
        issn = issn_element.text
    
    # Extract volume
    volume = ""
    volume_element = journal_element.find('.//JournalIssue/Volume')
    if volume_element is not None and volume_element.text:
        volume = volume_element.text
    
    # Extract issue
    issue = ""
    issue_element = journal_element.find('.//JournalIssue/Issue')
    if issue_element is not None and issue_element.text:
        issue = issue_element.text
    
    # Extract publication date
    pub_date = _parse_journal_date(journal_element)
    
    # Only create journal object if we have at least a title
    if title:
        return PubmedJournal(
            title=title,
            issn=issn,
            volume=volume,
            issue=issue,
            publication_date=pub_date
        )
    
    return None


def _parse_journal_date(journal_element: ET.Element) -> Optional[str]:
    """
    Parse journal publication date.
    
    Args:
        journal_element: XML element representing a journal
        
    Returns:
        Formatted date string or None
    """
    # This is a simplified implementation
    # A full implementation would parse the Year/Month/Day elements
    # and create a proper datetime object
    return None


def _parse_publication_date(article_element: ET.Element) -> Optional[str]:
    """
    Parse article publication date.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        Formatted date string or None
    """
    # This is a simplified implementation
    # A full implementation would parse the PubDate elements
    # and create a proper datetime object
    return None


def _parse_article_type(article_element: ET.Element) -> Optional[str]:
    """
    Parse article type from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        Article type string or None
    """
    # Look for PublicationType elements
    pub_type_elements = article_element.findall('.//PublicationTypeList/PublicationType')
    if pub_type_elements:
        # Return the first publication type
        if pub_type_elements[0].text:
            return pub_type_elements[0].text
    
    return None


def _parse_keywords(article_element: ET.Element) -> List[str]:
    """
    Parse keywords from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        List of keyword strings
    """
    keywords = []
    # PubMed doesn't typically have KeywordList in the standard format
    # Keywords are usually in MeshHeadingList or PublicationTypeList
    # For now, we'll return an empty list
    return keywords


def _parse_doi(article_element: ET.Element) -> Optional[str]:
    """
    Parse DOI from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        DOI string or None
    """
    # Look for DOI in ELocationID
    doi_element = article_element.find('.//ELocationID[@EIdType="doi"]')
    if doi_element is not None and doi_element.text:
        return doi_element.text
    
    # Also check in ArticleIdList
    doi_element = article_element.find('.//ArticleIdList/ArticleId[@IdType="doi"]')
    if doi_element is not None and doi_element.text:
        return doi_element.text
    
    return None


def _parse_language(article_element: ET.Element) -> Optional[str]:
    """
    Parse language from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        Language string or None
    """
    lang_element = article_element.find('.//Language')
    if lang_element is not None and lang_element.text:
        return lang_element.text
    
    return None


def _parse_country(article_element: ET.Element) -> Optional[str]:
    """
    Parse country from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        Country string or None
    """
    country_element = article_element.find('.//MedlineJournalInfo/Country')
    if country_element is not None and country_element.text:
        return country_element.text
    
    return None


def _parse_mesh_terms(article_element: ET.Element) -> List[str]:
    """
    Parse MeSH terms from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        List of MeSH term strings
    """
    mesh_terms = []
    mesh_elements = article_element.findall('.//MeshHeadingList/MeshHeading/DescriptorName')
    
    for mesh_element in mesh_elements:
        if mesh_element.text:
            mesh_terms.append(mesh_element.text)
    
    return mesh_terms


def _parse_chemicals(article_element: ET.Element) -> List[str]:
    """
    Parse chemicals from an article element.
    
    Args:
        article_element: XML element representing an article
        
    Returns:
        List of chemical strings
    """
    chemicals = []
    chemical_elements = article_element.findall('.//ChemicalList/Chemical/NameOfSubstance')
    
    for chemical_element in chemical_elements:
        if chemical_element.text:
            chemicals.append(chemical_element.text)
    
    return chemicals