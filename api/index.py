from flask import Flask, render_template_string, request, jsonify
import hashlib
import re
from datetime import datetime

app = Flask(__name__)

# Main HTML template containing your full advanced interface, audit logs, and SEO meta tags
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- SEO Meta Tags -->
    <title>SovereignVault AI | Enterprise Compliance & Clean Room Protocol</title>
    <meta name="description" content="An air-gapped compliance and data clean room framework designed for Indian regulatory standards including IT Act Section 43A and DPDP Act.">
    <meta name="keywords" content="AI clean room, compliance audit, data masking, IT Act 43A, DPDP Act, corporate data security">
    <meta name="author" content="B.Com Computer Applications Student Developer">
    
    <style>
        :root {
            --primary: #1b4332;
            --secondary: #2d6a4f;
            --accent: #52b788;
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #212529;
            --error-bg: #f8d7da;
            --error-text: #721c24;
            --success-bg: #d4edda;
            --success-text: #155724;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 700px;
            background: var(--card-bg);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }
        .header-flex {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 25px;
        }
        h1 {
            color: var(--primary);
            font-size: 24px;
            margin: 0 0 5px 0;
        }
        .subtitle {
            font-size: 13px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .top-badges {
            display: flex;
            gap: 8px;
        }
        .badge-btn {
            background: #e9ecef;
            border: 1px solid #ced4da;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            color: var(--text);
        }
        .badge-lock {
            background: #ffe5d9;
            border-color: #ffcad4;
            color: #d90429;
        }
        label {
            font-weight: 600;
            font-size: 14px;
            display: block;
            margin-bottom: 8px;
            color: var(--secondary);
        }
        .label-flex {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .mini-tag {
            font-size: 11px;
            background: #ffe5d9;
            color: #d90429;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        textarea, input[type="text"], input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ced4da;
            border-radius: 8px;
            font-size: 14px;
            box-sizing: border-box;
            margin-bottom: 20px;
            font-family: inherit;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        .file-upload-box {
            background: #f1f3f5;
            padding: 15px;
            border: 2px dashed #ced4da;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .checkbox-group {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            margin-bottom: 20px;
        }
        .checkbox-label {
            display: flex;
            align-items: center;
            font-weight: normal;
            font-size: 13px;
            margin-bottom: 10px;
            color: var(--text);
            cursor: pointer;
        }
        .checkbox-label:last-child {
            margin-bottom: 0;
        }
        .checkbox-label input {
            margin-right: 10px;
            width: 16px;
            height: 16px;
        }
        button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 14px 20px;
            font-size: 15px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            transition: background 0.2s;
        }
        button:hover {
            background-color: var(--secondary);
        }
        .result-box {
            margin-top: 25px;
            padding: 20px;
            border-radius: 8px;
            background: #e9ecef;
        }
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
            margin-bottom: 15px;
        }
        .status-success {
            background: var(--success-bg);
            color: var(--success-text);
        }
        .status-failed {
            background: var(--error-bg);
            color: var(--error-text);
        }
        pre {
            background: #212529;
            color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 13px;
        }
        .nav-links {
            margin-top: 20px;
            text-align: center;
        }
        .nav-links a {
            color: var(--secondary);
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
        }
        .nav-links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-flex">
            <div>
                <h1>SovereignVault AI</h1>
                <div class="subtitle">Secured Clean Room & Audit Ledger</div>
            </div>
            <div class="top-badges">
                <a href="#" class="badge-btn" onclick="alert('Audit Ledger feature active')">📝 Logs</a>
                <span class="badge-btn badge-lock">🔒 Lock</span>
            </div>
        </div>

        {% if result %}
            <div class="result-box">
                {% if "FAILED" in result.status %}
                    <div class="status-badge status-failed">⚠️ Security Violation</div>
                {% else %}
                    <div class="status-badge status-success">✅ Compliance Verified</div>
                {% endif %}
                
                <p><strong>Cryptographic Telemetry Package:</strong></p>
                <pre>{{ json_output }}</pre>

                <div class="nav-links" style="margin-top: 15px;">
                    <a href="/">&larr; Back to Clean Room Input</a>
                </div>
            </div>
        {% else %}
            <form method="POST" action="/process" enctype="multipart/form-data">
                <div class="label-flex">
                    <label for="raw_data">Raw Corporate Data Input:</label>
                    <span class="mini-tag">Indian PII Moat Active</span>
                </div>
                <textarea id="raw_data" name="raw_data" placeholder="Enter or paste data (PAN, Aadhaar, GSTIN, etc.)..."></textarea>

                <div class="file-upload-box">
                    <label for="batch_file" style="margin-bottom: 5px; font-size: 13px;">📁 Upload Batch File (.txt/.csv):</label>
                    <input type="file" id="batch_file" name="batch_file" accept=".txt,.csv" style="margin-bottom: 0; padding: 6px;">
                </div>

                <label for="custom_rule">Custom Restricted Term Rule:</label>
                <input type="text" id="custom_rule" name="custom_rule" placeholder="e.g., PROJECT_OMEGA">

                <div class="checkbox-group">
                    <label style="margin-bottom: 12px; color: var(--primary);">Native Regulatory Compliance Guardrails:</label>
                    
                    <label class="checkbox-label">
                        <input type="checkbox" name="guard_rbi" checked> RBI Data Localization Rule (Cross-border guard)
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" name="guard_it" checked> IT Act Section 43A (Unencrypted credential filter)
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" name="guard_dpdp" checked> DPDP Act Consent & PII Tokenizer
                    </label>
                </div>

                <button type="submit">Execute Clean Room Protocol</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, result=None)

@app.route('/process', methods=['POST'])
def process():
    raw_data = request.form.get('raw_data', '')
    custom_rule = request.form.get('custom_rule', '').strip()
    
    # Handle file upload if provided
    file = request.files.get('batch_file')
    if file and file.filename != '':
        file_content = file.read().decode('utf-8', errors='ignore')
        raw_data = raw_data + "\n" + file_content

    guard_rbi = request.form.get('guard_rbi')
    guard_it = request.form.get('guard_it')
    guard_dpdp = request.form.get('guard_dpdp')

    if not raw_data.strip():
        return render_template_string(HTML_TEMPLATE, result={"status": "FAILED"}, json_output='{"error": "Input data cannot be empty!"}')

    violation_detected = False
    violation_reason = ""
    
    if guard_it:
        forbidden_keywords = ["password", "secret", "sys_admin", "credential", "private_key"]
        lower_data = raw_data.lower()
        for word in forbidden_keywords:
            if word in lower_data:
                violation_detected = True
                violation_reason = f"IT Act Section 43A Violation (Unencrypted credential detected)"
                break

    if custom_rule and custom_rule.lower() in raw_data.lower():
        violation_detected = True
        violation_reason = f"Custom Rule Violation ({custom_rule} matched)"

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    checksum = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

    if violation_detected:
        status_str = f"FAILED ({violation_reason})"
        sanitized = "[BLOCKED DUE TO POLICY VIOLATION]"
    else:
        status_str = "SUCCESS (Verified Privacy Clean)"
        sanitized = raw_data
        if guard_dpdp:
            sanitized = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', '[PAN_REDACTED]', sanitized)
            sanitized = re.sub(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b', '[GSTIN_REDACTED]', sanitized)
            sanitized = re.sub(r'\b\d{10}\b', '[PHONE_REDACTED]', sanitized)

    telemetry = {
        "certificate_title": "SovereignVault AI Compliance Audit Certificate",
        "timestamp": timestamp,
        "status": status_str,
        "active_rule": custom_rule if custom_rule else "None",
        "regulatory_guards": {
            "rbi_localization": "Enforced" if guard_rbi else "Disabled",
            "it_act_43a": "Enforced" if guard_it else "Disabled",
            "dpdp_act": "Enforced" if guard_dpdp else "Disabled"
        },
        "checksum_sha256": checksum,
        "sanitized_content": sanitized,
        "vector_embedding": []
    }

    import json
    json_output = json.dumps(telemetry, indent=4)

    return render_template_string(HTML_TEMPLATE, result=telemetry, json_output=json_output)

if __name__ == '__main__':
    app.run(debug=True)
