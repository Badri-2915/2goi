-- 2GOI URL Shortener - Database Schema
-- Run this in the Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (synced with Supabase Auth)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    plan VARCHAR(20) DEFAULT 'free' NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Links table
CREATE TABLE IF NOT EXISTS links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_url TEXT NOT NULL,
    short_code VARCHAR(20) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    click_count INTEGER DEFAULT 0 NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMP
);

-- Clicks table
CREATE TABLE IF NOT EXISTS clicks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    link_id UUID NOT NULL REFERENCES links(id) ON DELETE CASCADE,
    country VARCHAR(10),
    browser VARCHAR(50),
    device_type VARCHAR(20),
    referrer VARCHAR(2048),
    ip_hash VARCHAR(64),
    clicked_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_links_short_code ON links(short_code);
CREATE INDEX IF NOT EXISTS idx_links_user_id ON links(user_id);
CREATE INDEX IF NOT EXISTS idx_links_is_active ON links(is_active);
CREATE INDEX IF NOT EXISTS idx_clicks_link_id ON clicks(link_id);
CREATE INDEX IF NOT EXISTS idx_clicks_clicked_at ON clicks(clicked_at);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Composite index for the most common query pattern (redirect lookup)
CREATE INDEX IF NOT EXISTS idx_links_code_active ON links(short_code, is_active);

-- Row Level Security (RLS) policies
ALTER TABLE links ENABLE ROW LEVEL SECURITY;
ALTER TABLE clicks ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own links
CREATE POLICY "Users can read own links" ON links
    FOR SELECT USING (user_id = auth.uid() OR user_id IS NULL);

-- Policy: Users can insert links
CREATE POLICY "Users can insert links" ON links
    FOR INSERT WITH CHECK (true);

-- Policy: Users can update their own links
CREATE POLICY "Users can update own links" ON links
    FOR UPDATE USING (user_id = auth.uid());

-- Policy: Users can read clicks on their links
CREATE POLICY "Users can read own clicks" ON clicks
    FOR SELECT USING (
        link_id IN (SELECT id FROM links WHERE user_id = auth.uid())
    );

-- Policy: System can insert clicks (via service role)
CREATE POLICY "System can insert clicks" ON clicks
    FOR INSERT WITH CHECK (true);

-- Policy: Users can read own profile
CREATE POLICY "Users can read own profile" ON users
    FOR SELECT USING (id = auth.uid());

-- Policy: System can insert users
CREATE POLICY "System can insert users" ON users
    FOR INSERT WITH CHECK (true);

-- Function to auto-create user on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email)
    VALUES (NEW.id, NEW.email)
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger: auto-create user on Supabase Auth signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
