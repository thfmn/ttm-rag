-- init.sql - Initialize PostgreSQL database tables for Thai Traditional Medicine RAG Bot

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create sources table
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    url TEXT,
    api_endpoint TEXT,
    access_method VARCHAR(50),
    reliability_score INTEGER CHECK (reliability_score >= 1 AND reliability_score <= 5),
    language VARCHAR(10) DEFAULT 'th',
    is_active BOOLEAN DEFAULT TRUE,
    source_metadata TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for sources table
CREATE INDEX IF NOT EXISTS idx_sources_name ON sources(name);
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(type);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    external_id VARCHAR(255),
    title TEXT,
    content TEXT,
    abstract TEXT,
    authors TEXT,
    publication_date TIMESTAMP WITH TIME ZONE,
    language VARCHAR(10),
    document_type VARCHAR(50),
    file_path TEXT,
    file_type VARCHAR(20),
    file_size INTEGER,
    processing_status VARCHAR(20) DEFAULT 'pending',
    quality_score FLOAT,
    validation_status VARCHAR(20) DEFAULT 'pending',
    document_metadata TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    embedding BYTEA
);

-- Create indexes for documents table
CREATE INDEX IF NOT EXISTS idx_documents_source_id ON documents(source_id);
CREATE INDEX IF NOT EXISTS idx_documents_external_id ON documents(external_id);
CREATE INDEX IF NOT EXISTS idx_documents_title_gin ON documents USING gin(title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_documents_publication_date ON documents(publication_date);

-- Create keywords table
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    term VARCHAR(255) NOT NULL UNIQUE,
    term_thai VARCHAR(255),
    category VARCHAR(100),
    frequency INTEGER DEFAULT 0,
    validated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for keywords table
CREATE INDEX IF NOT EXISTS idx_keywords_term ON keywords(term);
CREATE INDEX IF NOT EXISTS idx_keywords_term_thai ON keywords(term_thai);
CREATE INDEX IF NOT EXISTS idx_keywords_category ON keywords(category);

-- Create document_keyword_association table for many-to-many relationship
CREATE TABLE IF NOT EXISTS document_keyword_association (
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    PRIMARY KEY (document_id, keyword_id)
);

-- Create processing_logs table
CREATE TABLE IF NOT EXISTS processing_logs (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    process_type VARCHAR(50),
    status VARCHAR(20),
    message TEXT,
    execution_time VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    log_metadata TEXT
);

-- Create indexes for processing_logs table
CREATE INDEX IF NOT EXISTS idx_processing_logs_document_id ON processing_logs(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_logs_source_id ON processing_logs(source_id);
CREATE INDEX IF NOT EXISTS idx_processing_logs_process_type ON processing_logs(process_type);
CREATE INDEX IF NOT EXISTS idx_processing_logs_status ON processing_logs(status);
CREATE INDEX IF NOT EXISTS idx_processing_logs_created_at ON processing_logs(created_at);

-- Create initial sources
INSERT INTO sources (id, name, type, url, api_endpoint, access_method, reliability_score, source_metadata) VALUES
(1, 'PubMed', 'academic', 'https://pubmed.ncbi.nlm.nih.gov/', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils', 'api', 5, '{"api_key": null}');
INSERT INTO sources (id, name, type, url, api_endpoint, access_method, reliability_score, source_metadata) VALUES
(2, 'PMC Open Access', 'academic', 'https://www.ncbi.nlm.nih.gov/pmc/', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils', 'api', 5, '{"api_key": null}')
ON CONFLICT (id) DO NOTHING;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
DROP TRIGGER IF EXISTS update_sources_updated_at ON sources;
CREATE TRIGGER update_sources_updated_at 
    BEFORE UPDATE ON sources 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_keywords_updated_at ON keywords;
CREATE TRIGGER update_keywords_updated_at 
    BEFORE UPDATE ON keywords 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();