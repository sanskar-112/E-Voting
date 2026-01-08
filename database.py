import sqlite3
import os

DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create Voters Table (Stores Hashes)
    # Aadhar, Name, DOB, PIN are sensitive -> Store Hash
    # Email is needed for OTP -> Can store plain or hash? 
    # Requirement: "authorities... will not know about your personal detail"
    # But we need email to send OTP. 
    # Let's store email in plain text for the prototype to work (sending mail), 
    # or hash it and ask user to input email to verify?
    # The prompt says: "The system must then send an OTP... to the voter's registered email ID (the mail ID provided by the Election Commission)."
    # This implies the system HAS the email. 
    # However, "all sensitive data... is not encrypted... convert all sensitive data into a hash format".
    # If we hash email, we can't send mail. 
    # Compromise: Store email, but hash other personal details. 
    # Or maybe the "registered email ID" is stored separately or we assume the user inputs it and we verify the hash?
    # Prompt: "voter's registered email ID (the mail ID provided by the Election Commission)"
    # Let's store email as is, but hash Aadhar, Name, DOB, PIN.
    
    c.execute('''CREATE TABLE IF NOT EXISTS voters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aadhar_hash TEXT UNIQUE NOT NULL,
                    name_hash TEXT NOT NULL,
                    dob_hash TEXT NOT NULL,
                    pin_hash TEXT NOT NULL,
                    email TEXT NOT NULL,
                    has_voted INTEGER DEFAULT 0
                )''')

    # Create Parties Table
    c.execute('''CREATE TABLE IF NOT EXISTS parties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    party_name TEXT NOT NULL,
                    party_logo TEXT,
                    candidate_name TEXT NOT NULL,
                    candidate_pic TEXT,
                    vote_count INTEGER DEFAULT 0
                )''')

    # Create Votes Table (Blockchain Transactions)
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_hash TEXT NOT NULL,
                    block_index INTEGER NOT NULL,
                    party_id INTEGER NOT NULL,
                    timestamp REAL NOT NULL
                )''')

    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
