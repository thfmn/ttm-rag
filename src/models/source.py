from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Source:
    """
    Data class representing a data source
    """
    id: int
    name: str
    type: str  # 'government', 'academic', 'clinical', etc.
    url: Optional[str] = None
    api_endpoint: Optional[str] = None
    access_method: str = "api"  # 'api', 'scraping', 'manual'
    reliability_score: int = 3  # 1-5 scale
    language: str = "th"
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None