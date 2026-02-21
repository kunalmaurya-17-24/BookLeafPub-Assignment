
CREATE EXTENSION IF NOT EXISTS vector;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE IF NOT EXISTS author_status (
    email TEXT PRIMARY KEY,
    book_title TEXT NOT NULL,
    isbn TEXT UNIQUE,
    publishing_status TEXT,
    royalty_status TEXT,
    final_submission_date DATE,
    book_live_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_author_status_email ON author_status(email);


CREATE TABLE IF NOT EXISTS knowledge_base (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_embedding
ON knowledge_base
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);


CREATE OR REPLACE FUNCTION match_documents (
    query_embedding VECTOR(768),
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.content,
        kb.metadata,
        1 - (kb.embedding <=> query_embedding) AS similarity
    FROM knowledge_base kb
    ORDER BY kb.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

CREATE TABLE IF NOT EXISTS author_identities (
    id BIGSERIAL PRIMARY KEY,
    primary_email TEXT REFERENCES author_status(email) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    handle_or_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(platform, handle_or_id)
);


CREATE TABLE IF NOT EXISTS bot_logs (
    id BIGSERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    confidence_score FLOAT,
    platform_used TEXT,
    author_email TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);