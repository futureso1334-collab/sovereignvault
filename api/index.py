from flask import Flask, render_template_string, request
import sqlite3
import hashlib
import os

app = Flask(__name__)

DB_PATH = os.path.join('/tmp', 'sovereign_audit.db')

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action TEXT,
                hash_val TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

init_db()

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>SovereignVault RegTech</title>
            <style>
                body { font-family: monospace; background: #0d1117; color: #58a6ff; padding: 40px; }
                .box { border: 1px solid #30363d; padding: 20px; border-radius: 6px; background: #161b22; }
                input, button { background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 10px; margin-top: 10px; font-family: monospace; }
                button { cursor: pointer; background: #238636; color: white; border: none; }
            </style>
        </head>
        <body>
            <div class="box">
                <h2>SovereignVault RegTech Engine (Serverless Mode)</h2>
                <p>Status: Operational & Clean-room Secure</p>
                <form action="/api/index" method="POST">
                    <label>Audit Payload / Entry:</label><br>
                    <input type="text" name="payload" style="width: 100%;" placeholder="Enter compliance data..." required><br>
                    <button type="submit">Commit to Ledger</button>
                </form>
            </div>
        </body>
        </html>
    ''')

@app.route('/api/index', methods=['POST'])
@app.route('/secure-vault', methods=['POST'])
def secure_vault():
    payload = request.form.get('payload', '')
    payload_hash = hashlib.sha256(payload.encode()).hexdigest()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit_logs (action, hash_val) VALUES (?, ?)", (payload, payload_hash))
        conn.commit()
        
        cursor.execute("SELECT id, timestamp, action, hash_val FROM audit_logs ORDER BY id DESC LIMIT 5")
        logs = cursor.fetchall()
        conn.close()
    except Exception as e:
        logs = [(1, "Now", f"Error loading logs: {e}", "N/A")]
    
    logs_html = "".join([f"<li>[{row[1]}] <b>{row[2]}</b> (Hash: {row[3]})</li>" for row in logs])
    
    return render_template_string(f'''
        <!DOCTYPE html>
        <html>
        <head><title>Vault Secured</title><style>body {{ font-family: monospace; background: #0d1117; color: #58a6ff; padding: 40px; }}</style></head>
        <body>
            <h2>Audit Ledger Entry Committed</h2>
            <p><b>Hash:</b> {payload_hash}</p>
            <h3>Recent Ledger History:</h3>
            <ul>{logs_html}</ul>
            <br><a href="/" style="color: #58a6ff;">&larr; Back to Vault</a>
        </body>
        </html>
    ''')
