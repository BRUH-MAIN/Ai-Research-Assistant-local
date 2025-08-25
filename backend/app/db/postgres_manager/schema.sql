-- Active: 1756116113047@@127.0.0.1@5432@project
-- PostgreSQL schema with DROP IF EXISTS and indexes

DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS ai_analyses CASCADE;
DROP TABLE IF EXISTS session_papers CASCADE;
DROP TABLE IF EXISTS paper_tags CASCADE;
DROP TABLE IF EXISTS papers CASCADE;
DROP TABLE IF EXISTS ai_messages CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS session_participants CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS group_participants CASCADE;
DROP TABLE IF EXISTS groups CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    role TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE groups (
    group_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_by INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_groups_created_by ON groups(created_by);

CREATE TABLE group_participants (
    group_participant_id SERIAL PRIMARY KEY,
    group_id INT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role TEXT,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, user_id)
);
CREATE INDEX idx_group_participants_group_id ON group_participants(group_id);
CREATE INDEX idx_group_participants_user_id ON group_participants(user_id);

CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    group_id INT NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    created_by INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    topic TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);
CREATE INDEX idx_sessions_group_id ON sessions(group_id);
CREATE INDEX idx_sessions_created_by ON sessions(created_by);

CREATE TABLE session_participants (
    session_participant_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, user_id)
);
CREATE INDEX idx_session_participants_session_id ON session_participants(session_id);
CREATE INDEX idx_session_participants_user_id ON session_participants(user_id);

CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    sender_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);

CREATE TABLE ai_messages (
    ai_message_id SERIAL PRIMARY KEY,
    message_id INT NOT NULL UNIQUE REFERENCES messages(message_id) ON DELETE CASCADE,
    ai_type TEXT,
    metadata JSON
);
CREATE INDEX idx_ai_messages_message_id ON ai_messages(message_id);

CREATE TABLE papers (
    paper_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    authors TEXT,
    doi TEXT UNIQUE,
    published_at TIMESTAMP,
    source_url TEXT
);

CREATE TABLE paper_tags (
    tag_id SERIAL PRIMARY KEY,
    paper_id INT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    created_by INT REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_paper_tags_paper_id ON paper_tags(paper_id);
CREATE INDEX idx_paper_tags_created_by ON paper_tags(created_by);

CREATE TABLE session_papers (
    session_paper_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    paper_id INT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, paper_id)
);
CREATE INDEX idx_session_papers_session_id ON session_papers(session_id);
CREATE INDEX idx_session_papers_paper_id ON session_papers(paper_id);

CREATE TABLE ai_analyses (
    analysis_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    paper_id INT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    created_by INT REFERENCES users(user_id) ON DELETE SET NULL,
    analysis_type TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ai_analyses_session_id ON ai_analyses(session_id);
CREATE INDEX idx_ai_analyses_paper_id ON ai_analyses(paper_id);
CREATE INDEX idx_ai_analyses_created_by ON ai_analyses(created_by);

CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    given_by INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_feedback_session_id ON feedback(session_id);
CREATE INDEX idx_feedback_given_by ON feedback(given_by);
