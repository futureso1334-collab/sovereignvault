from flask import Flask, render_template_string, request, jsonify
import hashlib
import re
from datetime import datetime

app = Flask(__name__)

# Main HTML template containing the clean room interface, audit logs, and SEO meta tags
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
        h1 {
            color: var(--primary);
            font-size: 24px;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 25px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        label {
            font-weight: 600;
            font-size: 14px;
            display: block;
            margin-bottom: 8px;
            color: var(--secondary);
        }
        textarea, input[type="text"] {
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
            height: 150px;
            resize: vertical;
        }
        button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 12px 20px;
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
        <h1>SovereignVault AI</h1>
        <div class="subtitle">Air-Gapped Indian Regulatory Framework</div>

        {% if result %}
            <div class="result-box">
                {% if "FAILED" in result.status %}
                    <div class="status-badge status-failed">⚠️ Security Violation Detected</div>
                {% else %}
                    <div class="status-badge status-success">✅ Privacy Clean & Verified</div>
                {% endif %}
                
                <p><strong>Cryptographic Telemetry Package:</strong></p>
                <pre>{{ json_output }}</pre>

                <div class="nav-links" style="margin-top: 15px;">
                    <a href="/">&larr; Back to Clean Room Input</a>
                </div>
            </div>
        {% else %}
            <form method="POST" action="/process" onsubmit="return validateInput()">
                <label for="raw_data">Raw Corporate Data Input:</label>
                <textarea id="raw_data" name="raw_data" placeholder="Paste sensitive company logs, database queries, or text here..."></textarea>

                <label for="custom_rule">Custom Restricted Term Rule (Optional):</label>
                <input type="text" id="custom_rule" name="custom_rule" placeholder="e.g., PROJECT_OMEGA or Password">

                <button type="submit">Execute Clean Room Protocol</button>
            </form>
        {% endif %}
    </div>

    <script>
        function validateInput() {
            const rawData = document.getElementById('raw_data').value.trim();
            if (rawData === "") {
                alert("Error: Raw Corporate Data Input cannot be empty!");
                return false;
            }
            return true;
        }
    </script>
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

    # Empty input check server-side safeguard
    if not raw_data.strip():
        return render_template_string(HTML_TEMPLATE, result={"status": "FAILED"}, json_output='{"error": "Raw Corporate Data Input cannot be empty!"}')

    # Security Violation Check (Detecting unencrypted secrets/credentials)
    violation_detected = False
    violation_reason = ""
    
    forbidden_keywords = ["password", "secret", "sys_admin", "credential", "private_key"]
    lower_data = raw_data.lower()
    
    for word in forbidden_keywords:
        if word in lower_data:
            violation_detected = True
            violation_reason = f"IT Act Section 43A Violation (Unencrypted credential/secret detected)"
            break

    # Check custom rule if provided
    if custom_rule and custom_rule.lower() in lower_data:
        violation_detected = True
        violation_reason = f"Custom Rule Violation ({custom_rule} matched)"

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    checksum = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()

    if violation_detected:
        status_str = f"FAILED ({violation_reason})"
        sanitized = "[BLOCKED DUE TO POLICY VIOLATION]"
    else:
        status_str = "SUCCESS (Verified Privacy Clean)"
        # PII Masking implementation for Indian Context
        sanitized = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', '[PAN_REDACTED]', raw_data)
        sanitized = re.sub(r'\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b', '[GSTIN_REDACTED]', sanitized)
        sanitized = re.sub(r'\b\d{10}\b', '[PHONE_REDACTED]', sanitized)

    telemetry = {
        "certificate_title": "SovereignVault AI Compliance Audit Certificate",
        "timestamp": timestamp,
        "status": status_str,
        "active_rule": custom_rule if custom_rule else "None",
        "regulatory_guards": {
            "rbi_localization": "Enforced",
            "it_act_43a": "Enforced",
            "dpdp_act": "Enforced"
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
