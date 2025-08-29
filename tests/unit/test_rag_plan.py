"""
Test module for RAG implementation plan validation.
"""

import pytest
import os
from pathlib import Path

def test_rag_implementation_plan_exists():
    """Test that the RAG implementation plan documentation exists."""
    docs_path = Path(__file__).parent.parent.parent / "docs" / "rag_implementation_plan.md"
    assert docs_path.exists(), "RAG implementation plan documentation should exist"

def test_rag_implementation_plan_structure():
    """Test that the RAG implementation plan has the expected structure."""
    docs_path = Path(__file__).parent.parent.parent / "docs" / "rag_implementation_plan.md"
    
    with open(docs_path, "r") as f:
        content = f.read()
    
    # Check for key sections
    assert "# RAG Implementation Plan" in content
    assert "## Overview" in content
    assert "## Phase 1: Document Processing Pipeline" in content
    assert "## Phase 2: Similarity Search System" in content
    assert "## Phase 3: Basic Generation System" in content
    assert "## Phase 4: Comprehensive RAG System" in content
    
    # Check for evaluation and testing mentions
    assert "Evaluation" in content
    assert "Testing" in content
    assert "Analytics" in content
    assert "Documentation" in content

def test_rag_implementation_plan_in_index():
    """Test that the RAG implementation plan is included in the documentation index."""
    index_path = Path(__file__).parent.parent.parent / "docs" / "index.rst"
    
    with open(index_path, "r") as f:
        content = f.read()
    
    assert "rag_implementation_plan" in content

if __name__ == "__main__":
    pytest.main([__file__])