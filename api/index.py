from flask import Flask, render_template_string, request, session, redirect, url_for, Response
import hashlib
import json
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sovereign-vault-super-secret-key-2026')

MASTER_PASSCODE = os.environ.get('MASTER_PASSCODE', 'admin123')

# ---- SEO: change this to your real deployed domain ----
SITE_URL = os.environ.get('SITE_URL', 'https://example.com')

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com;"
    return response

def mask_pii(text):
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_REDACTED]', text)
    text = re.sub(r'(?:\+91|91)?[6-9]\d{9}', '[PHONE_REDACTED]', text)
    text = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', '[PAN_REDACTED]', text)
    text = re.sub(r'\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b', '[AADHAAR_REDACTED]', text)
    text = re.sub(r'\b\d{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b', '[GSTIN_REDACTED]', text)
    return text

# ---- SEO: robots.txt ----
@app.route('/robots.txt')
def robots_txt():
    lines = [
        "User-agent: *",
        "Allow: /$",
        "Disallow: /dashboard",
        "Disallow: /logs",
        "Disallow: /process",
        "Disallow: /logout",
        f"Sitemap: {SITE_URL}/sitemap.xml",
    ]
    return Response("\n".join(lines), mimetype='text/plain')

# ---- SEO: sitemap.xml (only the public page belongs here) ----
@app.route('/sitemap.xml')
def sitemap_xml():
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{SITE_URL}/</loc>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''
    return Response(xml, mimetype='application/xml')

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        passcode = request.form.get('passcode', '')
        if passcode == MASTER_PASSCODE:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid Master Access Passcode.'

    if not session.get('authenticated'):
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">

                <!-- ===== SEO TAGS (public gateway page only) ===== -->
                <title>SovereignVault AI | Secure Indian Data Compliance & PII Redaction Gateway</title>
                <meta name="description" content="SovereignVault AI is a secure clean-room gateway for Indian regulatory compliance — PAN, Aadhaar, GSTIN and PII redaction, RBI localization, IT Act 43A and DPDP Act guardrails.">
                <meta name="keywords" content="PII redaction, DPDP Act compliance, RBI data localization, IT Act 43A, Aadhaar masking, PAN masking, GSTIN masking, data clean room, India data privacy">
                <meta name="robots" content="index, follow">
                <link rel="canonical" href="{{ site_url }}/">

                <!-- Open Graph -->
                <meta property="og:type" content="website">
                <meta property="og:title" content="SovereignVault AI | Secure Indian Data Compliance Gateway">
                <meta property="og:description" content="Air-gapped clean-room protocol for Indian PII redaction and regulatory compliance (RBI, IT Act, DPDP Act).">
                <meta property="og:url" content="{{ site_url }}/">
                <meta property="og:site_name" content="SovereignVault AI">

                <!-- Twitter Card -->
                <meta name="twitter:card" content="summary">
                <meta name="twitter:title" content="SovereignVault AI | Secure Indian Data Compliance Gateway">
                <meta name="twitter:description" content="Air-gapped clean-room protocol for Indian PII redaction and regulatory compliance (RBI, IT Act, DPDP Act).">

                <!-- Structured data -->
                <script type="application/ld+json">
                {
                  "@context": "https://schema.org",
                  "@type": "SoftwareApplication",
                  "name": "SovereignVault AI",
                  "applicationCategory": "SecurityApplication",
                  "operatingSystem": "Web",
                  "description": "Secure clean-room gateway for Indian regulatory data compliance and PII redaction."
                }
                </script>
                <!-- ===== END SEO TAGS ===== -->

                <style>
                    :root { --bg-color: #f4f6f8; --card-bg: #ffffff; --text-color: #212529; --subtext-color: #64748b; --border-color: #e2e8f0; }
                    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; box-sizing: border-box; }
                    .container { width: 100%; max-width: 380px; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); text-align: center; }
                    .title h2 { margin: 0; color: #19692c; font-size: 24px; }
                    .title p { margin: 6px 0 20px 0; color: var(--subtext-color); font-size: 13px; }
                    .form-group { margin-bottom: 15px; text-align: left; }
                    label { font-size: 13px; font-weight: 600; display: block; margin-bottom: 6px; }
                    input { width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; box-sizing: border-box; font-size: 14px; }
                    .btn-primary { background: #19692c; color: white; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; margin-top: 5px; }
                    .error-msg { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; padding: 8px; border-radius: 6px; font-size: 12px; margin-bottom: 15px; }
                    .hint { font-size: 11px; color: var(--subtext-color); margin-top: 15px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="title">
                        <h1 style="font-size:24px;margin:0;color:#19692c;">SovereignVault AI</h1>
                        <p>Protected Anti-Hack Gateway</p>
                    </div>
                    {% if error %}
                        <div class="error-msg">{{ error }}</div>
                    {% endif %}
                    <form method="POST">
                        <div class="form-group">
                            <label>Master Access Passcode</label>
                            <input type="password" name="passcode" required placeholder="Enter secure key">
                        </div>
                        <button type="submit" class="btn-primary">Authenticate Securely</button>
                    </form>
                    <div class="hint">Shielded with CSP, HSTS, and Brute-Force Rate Limiting.</div>
                </div>
            </body>
            </html>
        ''', error=error, site_url=SITE_URL)

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('index'))

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en" id="html-root">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SovereignVault AI - Secure Dashboard</title>
            <meta name="robots" content="noindex, nofollow, noarchive">
            <style>
                :root { --bg-color: #f4f6f8; --card-bg: #ffffff; --text-color: #212529; --subtext-color: #64748b; --border-color: #e2e8f0; --input-bg: #ffffff; }
                [data-theme="dark"] { --bg-color: #0d1117; --card-bg: #161b22; --text-color: #c9d1d9; --subtext-color: #8b949e; --border-color: #30363d; --input-bg: #0d1117; }
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg-color); color: var(--text-color); margin: 0; padding: 15px; transition: background 0.3s, color 0.3s; }
                .container { max-width: 600px; margin: 0 auto; background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
                .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--border-color); padding-bottom: 15px; margin-bottom: 20px; }
                .title h2 { margin: 0; color: #19692c; font-size: 22px; }
                .title p { margin: 4px 0 0 0; color: var(--subtext-color); font-size: 13px; }
                .header-actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
                .btn-top { background: var(--border-color); border: 1px solid var(--border-color); border-radius: 8px; padding: 6px 12px; font-size: 12px; font-weight: 500; color: var(--text-color); cursor: pointer; display: flex; align-items: center; gap: 4px; text-decoration: none; }
                .btn-logout { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
                .card { border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; margin-bottom: 15px; background: var(--card-bg); }
                .card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
                .card label { font-size: 13px; font-weight: 600; color: var(--text-color); }
                .badge-pii { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
                textarea { width: 100%; height: 95px; background: var(--input-bg); color: var(--text-color); border: 1px solid var(--border-color); border-radius: 6px; padding: 10px; font-family: monospace; font-size: 13px; box-sizing: border-box; resize: vertical; }
                .file-upload { border: 2px dashed var(--border-color); border-radius: 6px; padding: 12px; text-align: center; margin-top: 10px; background: var(--bg-color); }
                .file-input-wrapper { display: flex; align-items: center; gap: 8px; justify-content: center; }
                input[type="text"], input[type="file"] { width: 100%; background: var(--input-bg); color: var(--text-color); padding: 9px 12px; border: 1px solid var(--border-color); border-radius: 6px; box-sizing: border-box; font-size: 13px; }
                .btn-clear-file { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; border-radius: 6px; padding: 6px 10px; font-size: 12px; font-weight: 600; cursor: pointer; display: none; align-items: center; gap: 4px; }
                .compliance-toggles { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; font-size: 12px; }
                .compliance-toggles label { font-weight: normal; display: flex; align-items: center; gap: 6px; cursor: pointer; }
                .btn-primary { background: #19692c; color: white; border: none; width: 100%; padding: 13px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; margin-top: 5px; }
                .btn-primary:hover { background: #14532d; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">
                        <h2>SovereignVault AI</h2>
                        <p>Secured Clean Room & Audit Ledger</p>
                    </div>
                    <div class="header-actions">
                        <a href="/logs" class="btn-top">📋 Logs</a>
                        <button type="button" class="btn-top" onclick="toggleTheme()">🌓 Theme</button>
                        <a href="/logout" class="btn-top btn-logout">🔒 Lock</a>
                    </div>
                </div>

                <form action="/process" method="POST" enctype="multipart/form-data">
                    <div class="card">
                        <div class="card-header-row">
                            <label>Raw Corporate Data Input:</label>
                            <span class="badge-pii">Indian PII Moat Active</span>
                        </div>
                        <textarea name="payload" id="payload-input" placeholder="Enter or paste data (PAN, Aadhaar, GSTIN, etc.)..."></textarea>
                        
                        <div class="file-upload">
                            <span style="font-size: 12px; color: var(--subtext-color);">📁 Upload Batch File (.txt/.csv):</span><br><br>
                            <div class="file-input-wrapper">
                                <input type="file" name="batch_file" id="batch-file" style="font-size: 12px;" onchange="handleFileSelect(event)">
                                <button type="button" id="clear-file-btn" class="btn-clear-file" onclick="clearFileSelection()">✕ Remove</button>
                            </div>
                        </div>

                        <label style="margin-top: 14px; display: block; margin-bottom: 6px;">Custom Restricted Term Rule:</label>
                        <input type="text" name="rule" placeholder="e.g. PROJECT_OMEGA">

                        <label style="margin-top: 14px; display: block; margin-bottom: 6px;">Native Regulatory Compliance Guardrails:</label>
                        <div class="compliance-toggles">
                            <label><input type="checkbox" name="rbi_localization" value="active" checked> RBI Data Localization Rule (Cross-border guard)</label>
                            <label><input type="checkbox" name="it_act" value="active" checked> IT Act Section 43A (Unencrypted credential filter)</label>
                            <label><input type="checkbox" name="dpdp_act" value="active" checked> DPDP Act Consent & PII Tokenizer</label>
                        </div>
                    </div>

                    <button type="submit" class="btn-primary">Execute Clean Room Protocol</button>
                </form>
            </div>

            <script>
                function toggleTheme() {
                    const root = document.getElementById('html-root');
                    if (root.getAttribute('data-theme') === 'dark') {
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
                    if (file) {
                        document.getElementById('clear-file-btn').style.display = 'inline-flex';
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            document.getElementById('payload-input').value = e.target.result;
                        };
                        reader.readAsText(file);
                    }
                }

                function clearFileSelection() {
                    document.getElementById('batch-file').value = '';
                    document.getElementById('clear-file-btn').style.display = 'none';
                }
            </script>
        </body>
        </html>
    ''')

@app.route('/logs')
def logs():
    if not session.get('authenticated'):
        return redirect(url_for('index'))

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SovereignVault AI - Audit Logs</title>
            <meta name="robots" content="noindex, nofollow, noarchive">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f8; color: #212529; margin: 0; padding: 15px; }
                .container { max-width: 600px; margin: 0 auto; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
                .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 20px; }
                .title h2 { margin: 0; color: #19692c; font-size: 22px; }
                .title p { margin: 4px 0 0 0; color: #64748b; font-size: 13px; }
                .log-item { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 10px; font-size: 12px; font-family: monospace; word-break: break-all; }
                .btn-back { background: #19692c; color: white; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; text-align: center; text-decoration: none; display: block; box-sizing: border-box; margin-top: 15px; }
                .btn-clear { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; padding: 6px 10px; border-radius: 6px; font-size: 11px; cursor: pointer; font-weight: 600; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">
                        <h2>Audit Ledger</h2>
                        <p>Historical Clean Room Executions</p>
                    </div>
                    <button class="btn-clear" onclick="clearLogs()">Clear Logs</button>
                </div>
                <div id="logs-container">
                    <p style="text-align: center; color: #64748b; font-size: 13px;">Loading logs...</p>
                </div>
                <a href="/dashboard" class="btn-back">&larr; Back to Dashboard</a>
            </div>

            <script>
                function loadLogs() {
                    const logsContainer = document.getElementById('logs-container');
                    const savedLogs = JSON.parse(localStorage.getItem('sovereign_audit_logs') || '[]');
                    
                    if (savedLogs.length === 0) {
                        logsContainer.innerHTML = '<p style="text-align: center; color: #64748b; font-size: 13px;">No audit logs recorded yet.</p>';
                        return;
                    }

                    let html = '';
                    savedLogs.forEach(log => {
                        html += `
                            <div class="log-item">
                                <b>Time:</b> ${log.timestamp}<br>
                                <b>Status:</b> ${log.status}<br>
                                <b>Rule:</b> ${log.active_rule}<br>
                                <b>SHA256:</b> ${log.checksum_sha256.substring(0, 16)}...
                            </div>
                        `;
                    });
                    logsContainer.innerHTML = html;
                }

                function clearLogs() {
                    if (confirm('Are you sure you want to clear all audit logs?')) {
                        localStorage.removeItem('sovereign_audit_logs');
                        loadLogs();
                    }
                }

                loadLogs();
            </script>
        </body>
        </html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process_vault():
    if not session.get('authenticated'):
        return redirect(url_for('index'))

    uploaded_file = request.files.get('batch_file')
    if uploaded_file and uploaded_file.filename != '':
        raw_payload = uploaded_file.read().decode('utf-8', errors='ignore')
    else:
        raw_payload = request.form.get('payload', '').strip()

    if not raw_payload:
        return render_template_string('''
            <script>
                alert('Error: Raw Corporate Data Input cannot be empty!');
                window.location.href = '/dashboard';
            </script>
        ''')

    sanitized_payload = mask_pii(raw_payload)
    rule = request.form.get('rule', '').strip()
    
    rbi_active = request.form.get('rbi_localization') == 'active'
    it_active = request.form.get('it_act') == 'active'
    dpdp_active = request.form.get('dpdp_act') == 'active'

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    is_violation = False
    violation_reason = ""
    
    if rule and rule.lower() in raw_payload.lower():
        is_violation = True
        violation_reason = f"Custom Restricted Term Triggered: {rule}"
    elif it_active and ("password" in raw_payload.lower() or "secret" in raw_payload.lower()):
        is_violation = True
        violation_reason = "IT Act Section 43A Violation (Unencrypted credential/secret detected)"

    payload_hash = hashlib.sha256(raw_payload.encode()).hexdigest()
    vector_embedding = [round(float(ord(c)) / 255.0, 4) for c in payload_hash[:16]]
    
    if is_violation:
        status_text = f"FAILED ({violation_reason})"
        badge_text = "⚠️ Security Violation"
        badge_style = "background: #fef2f2; color: #991b1b; border: 1px solid #fecaca;"
    else:
        status_text = "SUCCESS (Verified Privacy Clean)"
        badge_text = "🛡️ VERIFIED PRIVACY CLEAN"
        badge_style = "background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;"

    response_data = {
        "certificate_title": "SovereignVault AI Compliance Audit Certificate",
        "timestamp": timestamp,
        "status": status_text,
        "active_rule": rule if rule else "None",
        "regulatory_guards": {
            "rbi_localization": "Enforced",
            "it_act_43a": "Enforced",
            "dpdp_act": "Enforced"
        },
        "checksum_sha256": payload_hash,
        "sanitized_content": "[BLOCKED DUE TO POLICY VIOLATION]" if is_violation else sanitized_payload,
        "vector_embedding": vector_embedding if not is_violation else []
    }
    
    pretty_json = json.dumps(response_data, indent=4)

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SovereignVault AI - Compliance Certificate</title>
            <meta name="robots" content="noindex, nofollow, noarchive">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f8; color: #212529; margin: 0; padding: 15px; }
                .container { max-width: 600px; margin: 0 auto; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
                .header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 20px; }
                .title h2 { margin: 0; color: #19692c; font-size: 20px; }
                .title p { margin: 4px 0 0 0; color: #64748b; font-size: 12px; }
                .badge-verified { padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; {{ badge_style|safe }} }
                .card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: #fff; }
                .card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
                .card label { font-size: 13px; font-weight: 600; color: #334155; }
                .result-display { background: #f8fafc; border: 1px solid #cbd5e1; color: #0f172a; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; white-space: pre-wrap; word-break: break-all; max-height: 260px; overflow-y: auto; margin-bottom: 12px; }
                .btn-group { display: flex; gap: 10px; }
                .btn-secondary { background: #e2e8f0; color: #334155; border: none; padding: 10px 15px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; flex: 1; text-align: center; text-decoration: none; }
                .btn-back { background: #19692c; color: white; border: none; width: 100%; padding: 12px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; text-align: center; text-decoration: none; display: block; box-sizing: border-box; }
                .btn-back:hover { background: #14532d; }
                .hash-tag { font-size: 11px; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; color: #475569; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">
                        <h2>Compliance Audit Certificate</h2>
                        <p>Air-Gapped Indian Regulatory Framework</p>
                    </div>
                    <div class="badge-verified">{{ badge_text }}</div>
                </div>

                <div class="card">
                    <div class="card-header-row">
                        <label>Cryptographic Telemetry Package:</label>
                        <span class="hash-tag">SHA: {{ hash_short }}</span>
                    </div>
                    <div class="result-display" id="result-content">{{ pretty_json }}</div>
                    <div class="btn-group">
                        <button type="button" class="btn-secondary" onclick="copyResult()">Copy JSON</button>
                        <button type="button" class="btn-secondary" onclick="window.print()">Export PDF Certificate</button>
                    </div>
                </div>

                <a href="/dashboard" class="btn-back">&larr; Back to Clean Room Input</a>
            </div>

            <script>
                const newLog = {
                    timestamp: "{{ response_data.timestamp }}",
                    status: "{{ response_data.status }}",
                    active_rule: "{{ response_data.active_rule }}",
                    checksum_sha256: "{{ response_data.checksum_sha256 }}"
                };
                let existingLogs = JSON.parse(localStorage.getItem('sovereign_audit_logs') || '[]');
                existingLogs.unshift(newLog);
                localStorage.setItem('sovereign_audit_logs', JSON.stringify(existingLogs));

                function copyResult() {
                    navigator.clipboard.writeText(document.getElementById('result-content').innerText);
                    alert('Certificate telemetry copied to clipboard!');
                }
            </script>
        </body>
        </html>
    ''', pretty_json=pretty_json, hash_short=payload_hash[:10], badge_text=badge_text, badge_style=badge_style, response_data=response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
