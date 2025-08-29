# Future Steps

This section outlines our plans for future development of the project.

## Immediate Priorities (MVP Path)

With a functional RAG prototype now validated, our immediate focus shifts to addressing the key missing components identified in the CTO assessment to reach MVP readiness.

### 1. Implement Data Validation Pipeline
- **Priority**: Medium
- **Goal**: Ensure the quality and integrity of all data ingested into the RAG system.
- **Tasks**:
  - Develop a pipeline for data validation and quality scoring.
  - Implement deduplication and data normalization mechanisms.

### 2. Expand Data Sources
- **Priority**: High
- **Goal**: Mitigate the single-source dependency risk and enrich our knowledge base.
- **Tasks**:
  - Implement a connector for the PMC Open Access database.
  - Integrate at least one other Tier 1 source, such as the Thai Traditional Medicine Journal.

### 3. Integrate Generation Model
- **Priority**: High
- **Goal**: Complete the core RAG functionality by adding a text generation component.
- **Tasks**:
  - Integrate a suitable Large Language Model (e.g., from the Typhoon series).
  - Develop prompt engineering strategies for summarizing retrieved context into coherent answers.
  - Establish a framework for evaluating the quality and factual accuracy of generated responses.

## Medium-term Goals

Once the MVP is established, we will focus on enhancing the RAG system's capabilities and robustness.

### 1. Enhance RAG Performance
- Implement more advanced retrieval strategies (e.g., hybrid search).
- Fine-tune embedding models on Thai Traditional Medicine-specific texts.
- Optimize the generation process for quality, speed, and cost.

### 2. Production Monitoring & Optimization
- Implement a comprehensive monitoring stack with Grafana dashboards.
- Establish performance benchmarks and automated regression testing.
- Implement caching strategies for frequently accessed data.

## Long-term Goals

For the long-term success of the project, our vision includes:

### 2. Advanced Features
- Implement natural language querying
- Add document summarization capabilities
- Implement relationship mapping between documents
- Add recommendation systems for related documents
- Implement multi-hop reasoning capabilities

### 3. Scalability
- Implement distributed processing using Celery
- Add horizontal scaling capabilities
- Implement caching mechanisms for better performance
- Optimize database queries for large datasets
- Add load balancing for high availability

### 4. User Interface
- Develop a comprehensive web interface for the RAG bot
- Implement an API for external integrations
- Add administrative interface for managing sources and documents
- Create documentation and examples for users
- Implement user feedback collection mechanisms

## Success Metrics

We'll measure our progress using these success metrics:

### Data Acquisition Metrics
- **Coverage**: 10,000+ validated TTM documents/articles
- **Source Diversity**: 50+ unique authoritative sources
- **Quality Score**: 95%+ data validation rate
- **Pipeline Efficiency**: <24hr automated processing time
- **Documentation Coverage**: 100% of processes documented

### System Performance Metrics
- **Pipeline Throughput**: Documents processed per hour
- **Storage Efficiency**: Database size vs document count
- **API Response Times**: Average response time by source
- **System Uptime**: Pipeline availability percentage
- **Resource Utilization**: CPU, memory, and storage usage

### RAG Performance Metrics
- **Retrieval Accuracy**: Precision and recall of retrieved documents
- **Generation Quality**: Relevance and factual accuracy of generated responses
- **Response Time**: Latency for end-to-end RAG queries
- **User Satisfaction**: Feedback scores from evaluation tests
- **Evaluation Coverage**: Percentage of queries with evaluation data

## Revised Roadmap

Our development is now structured around enhancing the existing RAG prototype to prepare it for production.

### Phase 1: MVP Readiness (Current Phase)
- **Goal**: Address critical missing components for a viable product.
- **Key Tasks**:
  - [ ] Implement Data Validation Pipeline.
  - [ ] Add PMC Open Access as a new data source.
  - [ ] Integrate a generation model to complete the RAG loop.

### Phase 2: RAG Enhancement & Optimization
- **Goal**: Improve the performance, accuracy, and feature set of the RAG system.
- **Key Tasks**:
  - Implement advanced retrieval techniques (hybrid search).
  - Fine-tune embedding models for the TTM domain.
  - Add production-grade monitoring and performance dashboards.

### Phase 3: Scalability and User Interface
- **Goal**: Scale the system for wider use and provide a user-friendly interface.
- **Key Tasks**:
  - Implement distributed processing for data ingestion.
  - Develop a comprehensive web interface for end-users.
  - Build out an administrative dashboard for system management.
