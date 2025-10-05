#!/usr/bin/env python3
"""
Generate legal documents (Privacy Policy and Terms of Service) from configuration.
Creates production-ready, legally compliant documents based on your application's data practices.
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path


def format_list(items):
    """Format list items as markdown bullets"""
    if not items:
        return "- None specified"
    return "\n".join(f"- {item.replace('_', ' ').title()}" for item in items)


def generate_gdpr_section():
    """Generate GDPR-specific section"""
    return """
### EU Residents (GDPR)
Under the General Data Protection Regulation, you have the right to:
- Access your personal data
- Rectification of inaccurate data
- Erasure of your data ("right to be forgotten")
- Restriction of processing
- Data portability
- Object to processing
- Withdraw consent at any time

To exercise these rights, contact us at the email address provided below.
"""


def generate_ccpa_section():
    """Generate CCPA-specific section"""
    return """
### California Residents (CCPA)
Under the California Consumer Privacy Act, you have the right to:
- Know what personal information is collected
- Know whether your personal information is sold or disclosed
- Say no to the sale of personal information
- Access your personal information
- Request deletion of your personal information
- Equal service and price, even if you exercise your privacy rights

To exercise these rights, contact us at the email address provided below.
"""


def generate_privacy_policy(config, output_format='markdown'):
    """Generate privacy policy from config"""
    company = config['company']
    app = config['application']
    data = config['data_collection']
    usage = config['data_usage']
    rights = config.get('user_rights', {})
    compliance = config.get('compliance', {})

    policy = f"""# Privacy Policy for {company['name']}

**Effective Date:** {datetime.now().strftime('%B %d, %Y')}
**Last Updated:** {datetime.now().strftime('%B %d, %Y')}

## 1. Introduction

{company['name']} ("we," "us," or "our") operates {app['name']} (the "Service"). This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our Service available at {app.get('url', 'our application')}.

By using the Service, you agree to the collection and use of information in accordance with this policy.

## 2. Information We Collect

### 2.1 Personal Information

We collect the following personal information that you voluntarily provide:
{format_list(data.get('personal_data', []))}

### 2.2 Automatically Collected Information

We automatically collect certain information when you use our Service:
{format_list(data.get('device_data', []))}

### 2.3 Cookies and Tracking Technologies

{"We use cookies and similar tracking technologies to track activity on our Service and hold certain information. You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent." if data.get('cookies') else "We do not use cookies or tracking technologies."}

{"We use third-party analytics services to monitor and analyze the use of our Service." if data.get('analytics') else ""}

## 3. How We Use Your Information

We use the collected information for the following purposes:
{format_list(usage.get('purposes', []))}

## 4. How We Share Your Information

### 4.1 Third-Party Service Providers

We may share your information with third-party service providers who perform services on our behalf:
{format_list(usage.get('third_parties', []))}

### 4.2 International Data Transfers

{"We may transfer your personal information to countries outside your country of residence. We ensure appropriate safeguards are in place to protect your information in accordance with this Privacy Policy and applicable laws." if usage.get('international_transfers') else "We do not transfer data internationally."}

### 4.3 Legal Requirements

We may disclose your information if required by law or in response to valid requests by public authorities.

## 5. Your Privacy Rights

### 5.1 General Rights

You have the following rights regarding your personal data:
- **Access**: Request a copy of your personal data
- **Correction**: Request correction of inaccurate data
- **Deletion**: Request deletion of your personal data
- **Portability**: Request transfer of your data to another service
- **Opt-out**: Opt-out of marketing communications

{generate_gdpr_section() if compliance.get('gdpr') else ''}
{generate_ccpa_section() if compliance.get('ccpa') else ''}

## 6. Data Security

We implement appropriate technical and organizational security measures to protect your personal information. However, no method of transmission over the Internet or electronic storage is 100% secure.

## 7. Data Retention

We retain your personal information only for as long as necessary to fulfill the purposes outlined in this Privacy Policy, unless a longer retention period is required or permitted by law.

## 8. Children's Privacy

{"Our Service is not intended for children under 13. We do not knowingly collect personal information from children under 13. If you are a parent or guardian and believe your child has provided us with personal information, please contact us." if compliance.get('coppa') else ""}

## 9. Changes to This Privacy Policy

We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date.

## 10. Contact Us

If you have any questions about this Privacy Policy, please contact us:

- **Email**: {company['email']}
- **Address**: {company['address']}
- **Website**: {company.get('website', 'N/A')}

---

🤖 This document was generated with [Claude Code](https://claude.com/claude-code)
"""

    return policy


def generate_terms_of_service(config, output_format='markdown'):
    """Generate terms of service from config"""
    company = config['company']
    app = config['application']

    terms = f"""# Terms of Service for {app['name']}

**Effective Date:** {datetime.now().strftime('%B %d, %Y')}
**Last Updated:** {datetime.now().strftime('%B %d, %Y')}

## 1. Acceptance of Terms

By accessing or using {app['name']} (the "Service"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, do not use the Service.

These Terms apply to all users of the Service, including visitors, registered users, and contributors.

## 2. Service Description

{app['name']} is a {app.get('type', 'software')} service provided by {company['legal_name']} that allows users to {app.get('description', 'use our platform')}.

**Platforms**: {', '.join(app.get('platforms', ['web']))}

## 3. User Accounts

### 3.1 Registration

To access certain features of the Service, you may be required to create an account. You agree to:
- Provide accurate, current, and complete information
- Maintain and update your information
- Maintain the security of your account credentials
- Accept responsibility for all activities under your account
- Notify us immediately of any unauthorized access

### 3.2 Account Termination

We reserve the right to suspend or terminate your account at our discretion, without notice, for conduct that we believe violates these Terms or is harmful to other users, us, or third parties, or for any other reason.

## 4. Acceptable Use Policy

You agree NOT to:
- Violate any applicable laws or regulations
- Infringe on intellectual property rights of others
- Transmit any harmful code, viruses, or malware
- Attempt to gain unauthorized access to the Service
- Use the Service for any illegal or unauthorized purpose
- Harass, abuse, or harm other users
- Scrape, spider, or crawl the Service
- Reverse engineer or decompile the Service
- Interfere with the proper functioning of the Service

Violation of this policy may result in immediate termination of your account.

## 5. Intellectual Property

### 5.1 Your Content

You retain all ownership rights to content you submit, post, or display on the Service ("Your Content"). By submitting Your Content, you grant us a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, and distribute Your Content solely to provide and improve the Service.

You represent and warrant that:
- You own or have the necessary rights to Your Content
- Your Content does not violate any third-party rights
- Your Content complies with these Terms

### 5.2 Our Content

All content, features, and functionality of the Service (excluding Your Content) are owned by {company['legal_name']} and are protected by copyright, trademark, and other intellectual property laws.

You are granted a limited, non-exclusive, non-transferable license to access and use the Service for its intended purpose.

## 6. Payment Terms

{"""
### 6.1 Fees
Certain features of the Service may require payment. All fees are non-refundable unless otherwise stated.

### 6.2 Billing
You agree to provide accurate billing information and authorize us to charge your payment method for all fees incurred.

### 6.3 Subscription Cancellation
You may cancel your subscription at any time. Cancellation will be effective at the end of the current billing period.

### 6.4 Price Changes
We reserve the right to modify pricing with 30 days' notice to existing subscribers.
""" if app.get('type') == 'saas' else "This Service is provided free of charge."}

## 7. Disclaimers and Limitation of Liability

### 7.1 Disclaimer of Warranties

THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.

We do not warrant that:
- The Service will be uninterrupted, secure, or error-free
- Results obtained from the Service will be accurate or reliable
- Any errors in the Service will be corrected

### 7.2 Limitation of Liability

TO THE MAXIMUM EXTENT PERMITTED BY LAW, {company['legal_name'].upper()} SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES.

IN NO EVENT SHALL OUR TOTAL LIABILITY EXCEED THE AMOUNT YOU PAID US IN THE PAST TWELVE (12) MONTHS, OR $100, WHICHEVER IS GREATER.

## 8. Indemnification

You agree to indemnify, defend, and hold harmless {company['legal_name']}, its officers, directors, employees, and agents from any claims, liabilities, damages, losses, and expenses (including reasonable attorneys' fees) arising out of or in any way connected with:
- Your access to or use of the Service
- Your violation of these Terms
- Your violation of any third-party rights

## 9. Dispute Resolution

### 9.1 Governing Law

These Terms are governed by the laws of {company.get('country', 'the United States')}, without regard to conflict of law principles.

### 9.2 Arbitration

Any disputes arising from these Terms or the Service shall be resolved through binding arbitration, except that either party may seek injunctive relief in court.

### 9.3 Class Action Waiver

You agree to resolve disputes on an individual basis and waive the right to participate in class actions or class arbitrations.

## 10. Changes to Terms

We reserve the right to modify these Terms at any time. We will notify users of material changes by:
- Posting the updated Terms on the Service
- Updating the "Last Updated" date
- Sending email notification to registered users (for material changes)

Continued use of the Service after changes constitutes acceptance of the modified Terms.

## 11. Severability

If any provision of these Terms is found to be unenforceable or invalid, that provision shall be limited or eliminated to the minimum extent necessary, and the remaining provisions shall remain in full force and effect.

## 12. Entire Agreement

These Terms constitute the entire agreement between you and {company['legal_name']} regarding the Service and supersede all prior agreements and understandings.

## 13. Contact Information

For questions or concerns about these Terms, please contact us:

- **Email**: {company['email']}
- **Address**: {company['address']}
- **Website**: {company.get('website', 'N/A')}

---

🤖 This document was generated with [Claude Code](https://claude.com/claude-code)
"""

    return terms


def save_document(content, output_dir, filename, output_format):
    """Save generated document to file"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    ext = {'markdown': 'md', 'html': 'html', 'pdf': 'pdf'}[output_format]
    filepath = Path(output_dir) / f"{filename}.{ext}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✅ {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate legal documents from configuration'
    )
    parser.add_argument(
        'type',
        nargs='?',
        default='both',
        choices=['privacy', 'terms', 'both'],
        help='Type of document to generate (default: both)'
    )
    parser.add_argument(
        '--config',
        default='legal-config.json',
        help='Path to configuration JSON file (default: legal-config.json)'
    )
    parser.add_argument(
        '--format',
        default='markdown',
        choices=['markdown', 'html', 'pdf'],
        help='Output format (default: markdown)'
    )
    parser.add_argument(
        '--output',
        default='./legal/',
        help='Output directory (default: ./legal/)'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Show preview without saving'
    )

    args = parser.parse_args()

    # Load configuration
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Configuration file '{args.config}' not found")
        print("\nCreate a legal-config.json file with your company and application details.")
        print("See /home/hamel/.claude/commands/generate-legal.md for example configuration.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)

    # Validate required fields
    required_fields = ['company', 'application', 'data_collection', 'data_usage']
    missing_fields = [field for field in required_fields if field not in config]
    if missing_fields:
        print(f"❌ Error: Missing required fields in config: {', '.join(missing_fields)}")
        sys.exit(1)

    # Generate documents
    documents = {}

    if args.type in ['privacy', 'both']:
        print("📝 Generating Privacy Policy...")
        documents['privacy_policy'] = generate_privacy_policy(config, args.format)

    if args.type in ['terms', 'both']:
        print("📝 Generating Terms of Service...")
        documents['terms_of_service'] = generate_terms_of_service(config, args.format)

    # Preview or save
    if args.preview:
        for doc_name, content in documents.items():
            print(f"\n{'='*60}")
            print(f"PREVIEW: {doc_name.replace('_', ' ').title()}")
            print('='*60)
            print(content[:800] + "\n\n[... content truncated in preview ...]\n" if len(content) > 800 else content)
    else:
        print(f"\n💾 Saving documents to {args.output}")
        for doc_name, content in documents.items():
            save_document(content, args.output, doc_name, args.format)

        print(f"\n✅ Generated {len(documents)} document(s) in {args.output}")
        print("\n⚠️  LEGAL DISCLAIMER:")
        print("These documents are templates based on common practices.")
        print("They MUST be reviewed by a qualified attorney before use in production.")
        print("Laws vary by jurisdiction and change over time.")


if __name__ == '__main__':
    main()
