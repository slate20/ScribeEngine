-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test user (username: testuser, password: password123)
INSERT INTO users (username, password_hash) VALUES
    ('testuser', 'scrypt:32768:8:1$OhTY8rE77QY4MtSc$77cb268086ae09558d05ce5d3e7aec2ce5446e2b4c7170ba2e556fa0b371023eebdd540cc8317e17790bb7420f6c93e9553f7dd8b11a88454ab56f0952fa4134');
