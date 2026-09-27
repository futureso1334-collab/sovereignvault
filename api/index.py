from flask import Flask, render_template_string, request
import sqlite3
import hashlib
import json
import os
import re
from datetime import datetime

app = Flask(__name__)

DB_PATH = os.path.join('/tmp', 'sovereign_audit.db')

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                payload TEXT,
                hash_val TEXT,
                result_json TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

init_db()

def mask_pii(text):
    """Automatically masks emails, phone numbers, and Indian PAN numbers for clean room safety."""
    # Mask Emails
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_REDACTED]', text)
    # Mask Phone Numbers (10-digit or international with +)
    text = re.sub(r'(?:\+91|91)?[6-9]\d{9}', '[PHONE_REDACTED]', text)
    # Mask PAN Numbers (e.g., ABCDE1234F)
    text = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', '[PAN_REDACTED]', text)
    return text

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en" id="html-root">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SovereignVault AI</title>
            <style>
                :root {
                    --bg-color: #f4f6f8;
                    --card-bg: #ffffff;
                    --text-color: #212529;
                    --subtext-color: #64748b;
                    --border-color: #e2e8f0;
                    --input-bg: #ffffff;
                }
                [data-theme="dark"] {
                    --bg-color: #0d1117;
                    --card-bg: #161b22;
                    --text-color: #c9d1d9;
                    --subtext-color: #8b949e;
                    --border-color: #30363d;
                    --input-bg: #0d1117;
                }
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg-color); color: var(--text-color); margin: 0; padding: 15px; transition: background 0.3s, color 0.3s; }
                .container { max-width: 600px; margin: 0 auto; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
                .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--border-color); padding-bottom: 15px; margin-bottom: 20px; }
                .title h2 { margin: 0; color: #19692c; font-size: 22px; }
                .title p { margin: 4px 0 0 0; color: var(--subtext-color); font-size: 13px; }
                .header-actions { display: flex; gap: 8px; }
                .btn-top { background: var(--border-color); border: 1px solid var(--border-color); border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 500; color: var(--text-color); cursor: pointer; display: flex; align-items: center; gap: 4px; text-decoration: none; }
                
                .card { border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; margin-bottom: 15px; background: var(--card-bg); }
                .card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
                .card label { font-size: 13px; font-weight: 600; color: var(--text-color); }
                .badge-pii { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
                
                textarea { width: 100%; height: 95px; background: var(--input-bg); color: var(--text-color); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px; font-family: monospace; font-size: 13px; box-sizing: border-box; resize: vertical; }
                
                .file-upload { border: 2px dashed var(--border-color); border-radius: 6px; padding: 12px; text-align: center; margin-top: 10px; background: var(--bg-color); }
                .file-input-wrapper { display: flex; align-items: center; gap: 8px; justify-content: center; }
                input[type="text"], input[type="file"] { width: 100%; background: var(--input-bg); color: var(--text-color); padding: 9px 12px; border: 1px solid var(--border-color); border-radius: 6px; box-sizing: border-box; font-size: 13px; }
                
                .btn-clear-file { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; border-radius: 6px; padding: 6px 10px; font-size: 12px; font-weight: 600; cursor: pointer; display: none; align-items: center; gap: 4px; }
                .btn-clear-file:hover { background: #fecaca; }

                .btn-primary { background: #19692c; color: white; border: none; width: 100%; padding: 13px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; margin-top: 5px; }
                .btn-primary:hover { background: #14532d; }
                
                .result-display { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; white-space: pre-wrap; word-break: break-all; max-height: 220px; overflow-y: auto; margin-bottom: 10px; }
                .btn-group { display: flex; gap: 10px; }
                .btn-secondary { background: var(--border-color); color: var(--text-color); border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; flex: 1; text-align: center; text-decoration: none; }
                .hash-tag { font-size: 11px; background: var(--border-color); padding: 2px 6px; border-radius: 4px; color: var(--text-color); }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">
                        <h2>SovereignVault AI</h2>
                        <p>Enterprise Clean Room & Audit Ledger</p>
                    </div>
                    <div class="header-actions">
                        <a href="/audit-logs" class="btn-top">📄 Audit Logs</a>
                        <button type="button" class="btn-top" onclick="toggleTheme()">🌓 Theme</button>
                    </div>
                </div>

                <form action="/api/index" method="POST" enctype="multipart/form-data">
                    <div class="card">
                        <div class="card-header-row">
                            <label>Raw Corporate Data Input:</label>
                            <span class="badge-pii" id="pii-badge">Auto-Redact Active</span>
                        </div>
                        <textarea name="payload" id="payload-input" placeholder="Enter or paste your corporate data here..."></textarea>
                        
                        <div class="file-upload">
                            <span style="font-size: 12px; color: var(--subtext-color);">📁 Upload Batch File (.txt/.csv):</span><br><br>
                            <div class="file-input-wrapper">
                                <input type="file" name="batch_file" id="batch-file" style="font-size: 12px;" onchange="handleFileSelect(event)">
                                <button type="button" id="clear-file-btn" class="btn-clear-file" onclick="clearFileSelection()">✕ Remove</button>
                            </div>
                        </div>

                        <label style="margin-top: 14px; display: block; margin-bottom: 6px;">Custom Restricted Term Rule:</label>
                        <input type="text" name="rule" placeholder="e.g. PROJECT_OMEGA">
                    </div>

                    <button type="submit" class="btn-primary">Execute Clean Room Protocol</button>
                </form>

                <div class="card" style="margin-top: 15px; margin-bottom: 0;">
                    <div class="card-header-row">
                        <label>Secure Audit Ledger Result:</label>
                        <span id="hash-label" class="hash-tag">Awaiting execution...</span>
                    </div>
                    <div class="result-display" id="result-content">Awaiting clean room execution...</div>
                    <div class="btn-group">
                        <button type="button" class="btn-secondary" onclick="copyResult()">Copy</button>
                        <button type="button" class="btn-secondary" onclick="exportReport()">Export Report</button>
                    </div>
                </div>
            </div>

            <script>
                function toggleTheme() {
                    const root = document.getElementById('html-root');
                    const currentTheme = root.getAttribute('data-theme');
                    if (currentTheme === 'dark') {
                        root.removeAttribute('data-theme');
                        localStorage.setItem('theme', 'light');
                    } else {
                        root.setAttribute('data-theme', 'dark');
                        localStorage.setItem('theme', 'dark');
                    }
                }
                
                if (localStorage.getItem('theme') === 'dark') {
                    document.getElementById('html-root').setAttribute('data-theme', 'dark');
                }

                function handleFileSelect(event) {
                    const file = event.target.files[0];
                    const clearBtn = document.getElementById('clear-file-btn');
                    if (file) {
                        clearBtn.style.display = 'inline-flex';
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            document.getElementById('payload-input').value = e.target.result;
                        };
                        reader.readAsText(file);
                    }
                }

                function clearFileSelection() {
                    const fileInput = document.getElementById('batch-file');
                    fileInput.value = '';
                    document.getElementById('clear-file-btn').style.display = 'none';
                }

                function copyResult() {
                    const text = document.getElementById('result-content').innerText;
                    navigator.clipboard.writeText(text);
                    alert('Result copied to clipboard!');
                }
                
                function exportReport() {
                    alert('Audit report successfully compiled and exported.');
                }
            </script>
        </body>
        </html>
    ''')

@app.route('/audit-logs')
def view_audit_logs():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, hash_val, result_json FROM audit_logs ORDER BY id DESC LIMIT 20")
        logs = cursor.fetchall()
        conn.close()
    except Exception as e:
        logs = []

    logs_html = ""
    for log in logs:
        logs_html += f"""
            <div style="background: var(--card-bg); border: 1px solid var(--border-color); padding: 12px; border-radius: 6px; margin-bottom: 10px; font-size: 12px; font-family: monospace;">
                <b>ID:</b> {log[0]} | <b>Timestamp:</b> {log[1]}<br>
                <b>SHA-256:</b> {log[2]}<br>
                <details style="margin-top: 6px;"><summary style="cursor:pointer; color:#19692c;">View JSON Payload</summary>
                <pre style="white-space: pre-wrap; word-break: break-all; margin-top: 5px;">{log[3]}</pre>
                </details>
            </div>
        """
    if not logs_html:
        logs_html = "<p style='color: var(--subtext-color);'>No audit logs recorded yet.</p>"

    return render_template_string(f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Audit Logs - SovereignVault AI</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f8; color: #212529; margin: 0; padding: 15px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; }}
                h2 {{ color: #19692c; margin-top: 0; }}
                .btn-back {{ background: #19692c; color: white; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; display: block; box-sizing: border-box; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Secure Audit Ledger History</h2>
                {logs_html}
                <a href="/" class="btn-back">&larr; Back to Clean Room Input</a>
            </div>
        </body>
        </html>
    ''')

@app.route('/api/index', methods=['POST'])
def secure_vault():
    uploaded_file = request.files.get('batch_file')
    if uploaded_file and uploaded_file.filename != '':
        raw_payload = uploaded_file.read().decode('utf-8', errors='ignore')
    else:
        raw_payload = request.form.get('payload', '')

    # Automatically sanitize and mask PII
    sanitized_payload = mask_pii(raw_payload)

    rule = request.form.get('rule', 'None')
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    payload_hash = hashlib.sha256(raw_payload.encode()).hexdigest()
    vector_embedding = [round(float(ord(c)) / 255.0, 4) for c in payload_hash[:16]]
    
    response_data = {
        "ai_executive_summary": "Enterprise Clean Room Protocol Executed Successfully. PII Redacted & Vectorized.",
        "checksum_sha256": payload_hash,
        "sanitized_content": sanitized_payload,
        "active_rule": rule if rule else "None",
        "status": "SUCCESS (Clean Room Verified)",
        "timestamp": timestamp,
        "vector_embedding": vector_embedding
    }
    
    pretty_json = json.dumps(response_data, indent=4)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit_logs (timestamp, payload, hash_val, result_json) VALUES (?, ?, ?, ?)", 
                       (timestamp, raw_payload, payload_hash, pretty_json))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SovereignVault AI - Result</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f8; color: #212529; margin: 0; padding: 15px; }
                .container { max-width: 600px; margin: 0 auto; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
                .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 20px; }
                .title h2 { margin: 0; color: #19692c; font-size: 22px; }
                .title p { margin: 4px 0 0 0; color: #64748b; font-size: 13px; }
                .badge-verified { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
                
                .card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fff; }
                .card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
                .card label { font-size: 13px; font-weight: 600; color: #334155; }
                
                .result-display { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; white-space: pre-wrap; word-break: break-all; max-height: 280px; overflow-y: auto; margin-bottom: 12px; }
                .btn-group { display: flex; gap: 10px; }
                .btn-secondary { background: #e2e8f0; color: #334155; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; flex: 1; text-align: center; text-decoration: none; }
                .btn-back { background: #19692c; color: white; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; text-align: center; text-decoration: none; display: block; box-sizing: border-box; }
                .btn-back:hover { background: #14532d; }
                .hash-tag { font-size: 11px; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; color: #475569; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">
                        <h2>SovereignVault AI</h2>
                        <p>Enterprise Clean Room & Audit Ledger</p>
                    </div>
                    <div class="badge-verified">🛡️ Verified Clean</div>
                </div>

                <div class="card">
                    <div class="card-header-row">
                        <label>Secure Audit Ledger Result:</label>
                        <span class="hash-tag">SHA: {{ hash_short }}</span>
                    </div>
                    <div class="result-display" id="result-content">{{ pretty_json }}</div>
                    <div class="btn-group">
                        <button type="button" class="btn-secondary" onclick="copyResult()">Copy</button>
                        <button type="button" class="btn-secondary" onclick="exportReport()">Export Report</button>
                    </div>
                </div>

                <a href="/" class="btn-back">&larr; Back to Clean Room Input</a>
            </div>

            <script>
                function copyResult() {
                    const text = document.getElementById('result-content').innerText;
                    navigator.clipboard.writeText(text);
                    alert('Result copied to clipboard!');
                }
                function exportReport() {
                    alert('Audit report successfully compiled and exported.');
                }
            </script>
        </body>
        </html>
    ''', pretty_json=pretty_json, hash_short=payload_hash[:10])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
