"""
XML parsing utilities for PubMed Central (PMC) data.
"""

from typing import List, Optional
from xml.etree import ElementTree as ET
from src.models.pmc import PmcArticle, PmcAuthor
import logging

logger = logging.getLogger(__name__)

def parse_pmc_xml(xml_content: str) -> List[PmcArticle]:
    """
    Parse PMC XML content into a list of PmcArticle objects.
    """
    try:
        root = ET.fromstring(xml_content)
        articles = root.findall('.//article')
        parsed_articles = []
        for article_element in articles:
            try:
                parsed_article = _parse_single_pmc_article(article_element)
                parsed_articles.append(parsed_article)
            except Exception as e:
                logger.warning(f"Failed to parse PMC article: {e}")
                continue
        return parsed_articles
    except ET.ParseError as e:
        logger.error(f"Failed to parse PMC XML: {e}")
        raise

def _parse_single_pmc_article(article_element: ET.Element) -> PmcArticle:
    """
    Parse a single article element from PMC XML.
    """
    front = article_element.find('front')
    article_meta = front.find('article-meta') if front is not None else None

    if article_meta is None:
        raise ValueError("Missing <article-meta> in PMC article")

    pmcid = ""
    for article_id in article_meta.findall('.//article-id'):
        if article_id.get('pub-id-type') == 'pmc':
            if article_id.text:
                pmcid = article_id.text
                break

    if not pmcid:
        raise ValueError("Missing PMCID in PMC article")

    title = ""
    title_group = article_meta.find('title-group')
    if title_group is not None:
        title_element = title_group.find('article-title')
        if title_element is not None:
            title = "".join(title_element.itertext()).strip()

    abstract = ""
    abstract_element = article_meta.find('abstract')
    if abstract_element is not None:
        abstract = "".join(abstract_element.itertext()).strip()

    authors = _parse_pmc_authors(article_meta)

    journal = ""
    if front:
        journal_title_group = front.find('journal-meta/journal-title-group')
        if journal_title_group is not None:
            journal_title_element = journal_title_group.find('journal-title')
        if journal_title_element is not None and journal_title_element.text:
            journal = journal_title_element.text

    publication_year = None
    pub_date = article_meta.find('pub-date')
    if pub_date is not None:
        year_element = pub_date.find('year')
        if year_element is not None and year_element.text:
            try:
                publication_year = int(year_element.text)
            except (ValueError, TypeError):
                publication_year = None

    body = article_element.find('body')
    full_text = "".join(body.itertext()).strip() if body is not None else ""

    return PmcArticle(
        pmcid=pmcid,
        title=title,
        abstract=abstract,
        authors=authors,
        journal=journal,
        publication_year=publication_year,
        full_text=full_text,
    )

def _parse_pmc_authors(article_meta: ET.Element) -> List[PmcAuthor]:
    """
    Parse authors from PMC article metadata.
    """
    authors = []
    contrib_group = article_meta.find('contrib-group')
    if contrib_group is not None:
        for contrib in contrib_group.findall('contrib[@contrib-type="author"]'):
            name_element = contrib.find('name')
            if name_element is not None:
                surname = name_element.findtext('surname', '')
                given_names = name_element.findtext('given-names', '')
                name = f"{given_names} {surname}".strip()
                if name:
                    authors.append(PmcAuthor(name=name))
    return authors
