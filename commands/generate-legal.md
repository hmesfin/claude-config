---
name: generate-legal
description: Generate legal documents (Privacy Policy and Terms of Service) from configuration. Creates production-ready, legally compliant documents based on your application's data practices and business model.
---

# /generate-legal Command

Generate Privacy Policy and Terms of Service documents from configuration files.

## Usage

```bash
/generate-legal [type] [options]
```

## Arguments

- `privacy` - Generate Privacy Policy only
- `terms` - Generate Terms of Service only
- `both` - Generate both documents (default)

## Options

- `--config <path>` - Path to configuration JSON file (default: `legal-config.json`)
- `--format <format>` - Output format: `markdown`, `html`, `pdf` (default: `markdown`)
- `--output <path>` - Output directory (default: `./legal/`)
- `--preview` - Show preview without saving

## Examples

```bash
# Generate both documents with default config
/generate-legal both

# Generate only privacy policy
/generate-legal privacy --format html

# Use custom config
/generate-legal both --config my-legal-config.json

# Preview before saving
/generate-legal both --preview
```

## Configuration File

Create `legal-config.json`:

```json
{
  "company": {
    "name": "TechCorp Inc.",
    "legal_name": "TechCorp Incorporated",
    "address": "123 Main St, San Francisco, CA 94105",
    "country": "USA",
    "email": "legal@techcorp.com",
    "website": "https://techcorp.com"
  },

  "application": {
    "name": "TechApp",
    "type": "saas",
    "url": "https://app.techcorp.com",
    "platforms": ["web", "ios", "android"]
  },

  "data_collection": {
    "personal_data": ["name", "email", "phone"],
    "device_data": ["ip_address", "browser", "device_id"],
    "cookies": true,
    "analytics": true
  },

  "data_usage": {
    "purposes": ["service_provision", "analytics", "marketing"],
    "third_parties": ["hosting", "analytics", "email"],
    "international_transfers": true
  },

  "user_rights": {
    "access": true,
    "deletion": true,
    "portability": true,
    "opt_out": true
  },

  "compliance": {
    "gdpr": true,
    "ccpa": true,
    "coppa": false
  }
}
```

## Generated Output

### Privacy Policy Sections

```markdown
# Privacy Policy for TechCorp Inc.

**Effective Date:** January 1, 2025
**Last Updated:** January 1, 2025

## 1. Introduction
[Company introduction and commitment to privacy]

## 2. Information We Collect
### Personal Information
- Name, email address, phone number

### Automatically Collected Information
- IP address, browser type, device identifiers

### Cookies and Tracking
[Cookie usage and opt-out options]

## 3. How We Use Your Information
- Service provision and improvement
- Analytics and performance monitoring
- Marketing communications (with consent)

## 4. How We Share Your Information
### Service Providers
- Hosting: [Provider names]
- Analytics: [Provider names]
- Email: [Provider names]

### International Transfers
[Data transfer mechanisms and safeguards]

## 5. Your Privacy Rights
### For All Users
- Right to access your data
- Right to delete your data
- Right to data portability
- Right to opt-out of marketing

### California Residents (CCPA)
[California-specific rights]

### EU Residents (GDPR)
[GDPR-specific rights]

## 6. Data Security
[Security measures and breach procedures]

## 7. Contact Us
Email: legal@techcorp.com
Address: 123 Main St, San Francisco, CA 94105
```

### Terms of Service Sections

```markdown
# Terms of Service for TechApp

**Effective Date:** January 1, 2025

## 1. Acceptance of Terms
[Agreement formation]

## 2. Service Description
[What the service provides]

## 3. User Accounts
[Registration, security, termination]

## 4. Acceptable Use Policy
[Prohibited activities and consequences]

## 5. Intellectual Property
### Your Content
[User content license]

### Our Content
[Company IP and user license]

## 6. Payment Terms
[Pricing, billing, refunds]

## 7. Disclaimers and Limitation of Liability
[Legal protections]

## 8. Dispute Resolution
[Governing law, arbitration, venue]

## 9. Changes to Terms
[Amendment procedures]

## 10. Contact Information
[Legal contact details]
```

## Implementation

```python
import json
from datetime import datetime
from pathlib import Path

def generate_legal(doc_type='both', config_path='legal-config.json', format='markdown', output_dir='./legal', preview=False):
    """Generate legal documents"""

    # Load configuration
    with open(config_path) as f:
        config = json.load(f)

    # Generate documents
    documents = {}

    if doc_type in ['privacy', 'both']:
        documents['privacy_policy'] = generate_privacy_policy(config, format)

    if doc_type in ['terms', 'both']:
        documents['terms_of_service'] = generate_terms_of_service(config, format)

    # Preview or save
    if preview:
        for doc_name, content in documents.items():
            print(f"\n{'='*50}")
            print(f"PREVIEW: {doc_name.replace('_', ' ').title()}")
            print('='*50)
            print(content[:500] + "..." if len(content) > 500 else content)
    else:
        save_documents(documents, output_dir, format)
        print(f"✅ Generated {len(documents)} document(s) in {output_dir}/")

def generate_privacy_policy(config, format='markdown'):
    """Generate privacy policy from config"""

    company = config['company']
    app = config['application']
    data = config['data_collection']
    usage = config['data_usage']
    rights = config['user_rights']
    compliance = config['compliance']

    # Build document
    policy = f"""
# Privacy Policy for {company['name']}

**Effective Date:** {datetime.now().strftime('%B %d, %Y')}
**Last Updated:** {datetime.now().strftime('%B %d, %Y')}

## 1. Introduction

{company['name']} ("we," "us," or "our") operates {app['name']} (the "Service"). This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our Service.

## 2. Information We Collect

### Personal Information
We collect the following personal information:
{format_list(data.get('personal_data', []))}

### Automatically Collected Information
We automatically collect:
{format_list(data.get('device_data', []))}

### Cookies and Tracking Technologies
{"We use cookies and similar tracking technologies." if data.get('cookies') else "We do not use cookies."}

## 3. How We Use Your Information

We use your information for:
{format_list(usage.get('purposes', []))}

## 4. How We Share Your Information

### Third-Party Service Providers
We share data with:
{format_list(usage.get('third_parties', []))}

{"### International Data Transfers\nWe transfer data internationally with appropriate safeguards." if usage.get('international_transfers') else ""}

## 5. Your Privacy Rights

You have the right to:
- Access your personal data
- Request deletion of your data
- Data portability
- Opt-out of marketing communications

{generate_gdpr_section() if compliance.get('gdpr') else ''}
{generate_ccpa_section() if compliance.get('ccpa') else ''}

## 6. Data Security

We implement appropriate technical and organizational measures to protect your data.

## 7. Contact Us

For privacy-related questions:
- Email: {company['email']}
- Address: {company['address']}

---

🤖 This document was generated with [Claude Code](https://claude.com/claude-code)
"""

    if format == 'html':
        return markdown_to_html(policy)
    elif format == 'pdf':
        return markdown_to_pdf(policy)

    return policy

def generate_terms_of_service(config, format='markdown'):
    """Generate terms of service from config"""

    company = config['company']
    app = config['application']

    terms = f"""
# Terms of Service for {app['name']}

**Effective Date:** {datetime.now().strftime('%B %d, %Y')}

## 1. Acceptance of Terms

By accessing {app['name']}, you agree to be bound by these Terms of Service.

## 2. Service Description

{app['name']} is a {app['type']} service provided by {company['legal_name']}.

## 3. User Accounts

You are responsible for:
- Maintaining account security
- All activity under your account
- Notifying us of unauthorized access

## 4. Acceptable Use Policy

You may not:
- Violate any laws or regulations
- Infringe on intellectual property rights
- Transmit harmful code or malware
- Attempt unauthorized access

## 5. Intellectual Property

### Your Content
You retain ownership of content you create. You grant us a license to use your content to provide the Service.

### Our Content
All Service content, features, and functionality are owned by {company['legal_name']}.

## 6. Disclaimer of Warranties

THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND.

## 7. Limitation of Liability

{company['legal_name']} SHALL NOT BE LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES.

## 8. Governing Law

These Terms are governed by the laws of {company['country']}.

## 9. Changes to Terms

We may modify these Terms. Continued use constitutes acceptance.

## 10. Contact

For questions about these Terms:
- Email: {company['email']}
- Address: {company['address']}

---

🤖 This document was generated with [Claude Code](https://claude.com/claude-code)
"""

    if format == 'html':
        return markdown_to_html(terms)
    elif format == 'pdf':
        return markdown_to_pdf(terms)

    return terms

def save_documents(documents, output_dir, format):
    """Save generated documents"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for doc_name, content in documents.items():
        ext = {'markdown': 'md', 'html': 'html', 'pdf': 'pdf'}[format]
        filepath = Path(output_dir) / f"{doc_name}.{ext}"

        with open(filepath, 'w') as f:
            f.write(content)

        print(f"  ✅ {filepath}")
```

## Compliance Notes

**⚠️ Legal Disclaimer:**
- These are **template documents** based on common practices
- They should be reviewed by a lawyer before use in production
- Laws vary by jurisdiction and change over time
- Consult legal counsel for compliance with:
  - GDPR (EU)
  - CCPA/CPRA (California)
  - COPPA (Children's privacy)
  - Industry-specific regulations

## Advanced Usage

### Custom Templates

Place custom templates in `/home/hamel/.claude/templates/legal/`:

```
templates/legal/
  ├── privacy_policy.md.j2
  └── terms_of_service.md.j2
```

### Multi-Language Support

```bash
/generate-legal both --config legal-config.json --lang en,es,fr
```

### Integration with CI/CD

```yaml
- name: Generate Legal Documents
  run: /generate-legal both --config legal-config.json
  if: github.ref == 'refs/heads/main'
```

This command provides a quick way to generate standard legal documents, but always have them reviewed by legal counsel before publishing.
