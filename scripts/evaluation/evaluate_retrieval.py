import json
import time
from pathlib import Path
import requests

# Configuration
API_ENDPOINT = "http://localhost:8005/api/v1/rag/query"
HEADERS = {"Content-Type": "application/json"}
OUTPUT_DIR = Path("results")
OUTPUT_FILE = OUTPUT_DIR / "retrieval_evaluation_results.json"

# A set of questions to evaluate the retrieval quality.
# These are designed to be answerable by the ingested documents.
EVALUATION_QUESTIONS = [
    "What are the benefits of Thai traditional medicine for mental health?",
    "What is the role of 'Pra-pai-ro-ma-sa-ma-nee' formula in treating fever?",
    "What are the anti-inflammatory properties of 'Plai' (Zingiber cassumunar)?",
    "How is 'Look-pra-kob' (herbal compress ball) used in Thai medicine?",
    "What does the evidence say about the effectiveness of 'Fah-talai-jone' (Andrographis paniculata) for COVID-19?",
    "What are the common uses of 'Rang-jeud' (Thunbergia laurifolia) in detoxification?",
    "What is the scientific evidence for the use of 'Ka-min-chan' (Curcuma longa) in treating digestive issues?",
    "Describe the 'Sen Sib' energy lines in Thai massage.",
    "What are the traditional uses of 'Ma-kham-pom' (Phyllanthus emblica)?",
    "How does Thai herbal medicine approach the treatment of diabetes?",
]

def main():
    """
    Evaluates the RAG retrieval system by posing a set of questions and logging the results.
    """
    print("Starting retrieval evaluation...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    total_time = 0

    for i, question in enumerate(EVALUATION_QUESTIONS):
        print(f"\nQuerying with question {i + 1}/{len(EVALUATION_QUESTIONS)}: '{question}'")
        
        payload = {
            "query": question,
            "top_k": 5,
            "return_context": True
        }

        start_time = time.time()
        try:
            response = requests.post(API_ENDPOINT, headers=HEADERS, data=json.dumps(payload))
            response.raise_for_status()
            
            end_time = time.time()
            query_time = end_time - start_time
            total_time += query_time
            
            response_data = response.json()
            
            retrieved_chunks = response_data.get("context")
            if retrieved_chunks is None:
                retrieved_chunks = []

            print(f"Retrieved {len(retrieved_chunks)} chunks in {query_time:.2f} seconds.")

            results.append({
                "question": question,
                "query_time_seconds": query_time,
                "answer": response_data.get("answer"),
                "retrieved_context": retrieved_chunks,
            })

        except requests.exceptions.RequestException as e:
            print(f"Failed to query for question '{question}': {e}")
            results.append({
                "question": question,
                "error": str(e)
            })

    print(f"\nTotal query time for all questions: {total_time:.2f} seconds.")
    
    # Save the results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Evaluation results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
