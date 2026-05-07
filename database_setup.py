import sqlite3
import os

DB_NAME = "submission_review.db"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    
    cursor.executescript("""
        DROP TABLE IF EXISTS submissions;
        DROP TABLE IF EXISTS reviewers;
        DROP TABLE IF EXISTS reviews;
    """)
    
    
    cursor.execute("""
        CREATE TABLE submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    
    cursor.execute("""
        CREATE TABLE reviewers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            max_workload INTEGER DEFAULT 5,
            current_workload INTEGER DEFAULT 0,
            conflict_subject TEXT
        )
    """)
    
    
    cursor.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER,
            reviewer_id INTEGER,
            score INTEGER,
            comment TEXT,
            FOREIGN KEY (submission_id) REFERENCES submissions(id),
            FOREIGN KEY (reviewer_id) REFERENCES reviewers(id)
        )
    """)
    
    # sample reviewers 
    reviewers = [
        ("Alice", "alice@example.com", 5, 0, "AI"),
        ("Bob", "bob@example.com", 5, 2, "ML"),
        ("Carol", "carol@example.com", 3, 1, ""),
        ("David", "david@example.com", 4, 0, "Security"),
        ("Eve", "eve@example.com", 5, 3, "")
    ]
    cursor.executemany("""
        INSERT INTO reviewers (name, email, max_workload, current_workload, conflict_subject)
        VALUES (?, ?, ?, ?, ?)
    """, reviewers)
    
    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()