from flask import Flask, render_template_string, request, session, redirect, url_for
import hashlib
import json
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sovereign-vault-super-secret-key-2026')

MASTER_PASSCODE = os.environ.get('MASTER_PASSCODE', 'admin123')

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headersHere is your complete, updated master Python script for `api/index.py`. 

I have added the missing input validation check right at the start of the `/process` route so that if someone clicks **Execute Clean Room Protocol** with an empty input box and no file attached, it will immediately pop up an error alert and safely redirect them back to the dashboard instead of generating a blank certificate.

```python
from flask import Flask, render_template_string, request, session, redirect, url_for
import hashlib
import json
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sovereign-vault-super-secret-key-2026')

MASTER_PASSCODE = os.environ.get('MASTER_PASSCODE', 'admin123')

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' [https://fonts.googleapis.com](https://fonts.googleapis.com) [https://fonts.gstatic.com](https://fonts.gstatic.com);"
    return response

def mask_pii(text):
    # Standard PII & Indian PII Moat (PAN, Aadhaar, GSTIN, Email, Phone)
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL_REDACTED]', text)
    text = re.sub(r'(?:\+91|91)?[6-9]\d{9}', '[PHONE_REDACTED]', text)
    text = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', '[PAN_REDACTED]', text)
    text = re.sub(
