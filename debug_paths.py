import sys
from pathlib import Path

# Print current working directory
print(f"Current working directory: {Path.cwd()}")

# Print script location
print(f"Script location: {Path(__file__).parent}")

# Check if rag module exists
rag_module_path = Path(__file__).parent / "src" / "rag"
print(f"Looking for RAG module at: {rag_module_path}")
print(f"RAG module exists: {rag_module_path.exists()}")

# List contents of rag directory if it exists
if rag_module_path.exists():
    print("Contents of RAG directory:")
    for item in rag_module_path.iterdir():
        print(f"  {item.name}")

# Check if docs directory exists
docs_path = Path(__file__).parent / "docs"
print(f"Docs directory exists: {docs_path.exists()}")

# Check for specific documentation files
if docs_path.exists():
    doc_files = [
        "rag_implementation_plan.md",
        "rag_kickoff_summary.md", 
        "final_summary.md"
    ]
    
    for doc_file in doc_files:
        doc_file_path = docs_path / doc_file
        print(f"{doc_file} exists: {doc_file_path.exists()}")