"""
Input sanitization utilities for the Thai Traditional Medicine RAG Bot API.
"""

import nh3
from typing import Optional, List, Union

def sanitize_text(text: str) -> str:
    """
    Sanitize text input to prevent XSS attacks using nh3 (Python binding for ammonia).
    
    Args:
        text (str): The text to sanitize
        
    Returns:
        str: The sanitized text
    """
    if not text:
        return text
    
    # Remove any HTML tags and attributes using nh3
    clean_text = nh3.clean(
        text,
        tags=set(),  # No allowed tags
        attributes={}  # No allowed attributes
    )
    
    # Limit the length of the text
    max_length = 1000
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length]
    
    return clean_text

def sanitize_query(query: str) -> str:
    """
    Sanitize search query input.
    
    Args:
        query (str): The search query to sanitize
        
    Returns:
        str: The sanitized query
    """
    if not query:
        return query
    
    # Sanitize the text
    clean_query = sanitize_text(query)
    
    # Remove any control characters that might cause issues
    clean_query = ''.join(char for char in clean_query if ord(char) >= 32 or char in '\\n\\r\\t')
    
    return clean_query

def sanitize_list(items: List[str]) -> List[str]:
    """
    Sanitize a list of text items.
    
    Args:
        items (List[str]): The list of items to sanitize
        
    Returns:
        List[str]: The list of sanitized items
    """
    if not items:
        return items
    
    return [sanitize_text(item) for item in items]
