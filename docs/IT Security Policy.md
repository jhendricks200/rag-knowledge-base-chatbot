# Meridian Technologies — IT Security Policy

Document Classification: Internal | Last Updated: February 15, 2026 | Owner: Information Security Team

## Purpose

This policy establishes the security requirements for all Meridian Technologies employees, contractors, and third-party users who access company systems, data, or networks. Compliance with this policy is mandatory and is a condition of employment.

## Password and Authentication

### Password Requirements

All accounts must use passwords that meet the following criteria:
- Minimum 14 characters
- Must include at least one uppercase letter, one lowercase letter, one number, and one special character
- Cannot reuse any of the last 12 passwords
- Must be changed every 90 days (prompted automatically)
- Cannot contain your name, username, or common dictionary words

### Multi-Factor Authentication (MFA)

MFA is required for all company accounts without exception. Approved MFA methods:
- **Preferred**: Hardware security key (YubiKey — provided by IT)
- **Acceptable**: Authenticator app (Google Authenticator or Authy)
- **Not permitted**: SMS-based authentication (vulnerable to SIM-swapping attacks)

Employees receive a YubiKey during onboarding. Lost keys must be reported to IT immediately at helpdesk@meridiantech.com. A temporary authenticator app code will be issued while a replacement key is shipped (within 2 business days).

### Account Lockout

Accounts are locked after 5 consecutive failed login attempts. Locked accounts can be unlocked by IT after identity verification, or automatically after 30 minutes.

## Device Security

### Company Devices

All company-issued devices must have the following:
- FileVault (Mac) or BitLocker (Windows) full-disk encryption enabled
- CrowdStrike Falcon endpoint protection installed and running
- Automatic OS updates enabled (updates applied within 7 days of release)
- Screen lock after 5 minutes of inactivity
- Find My Device enabled for remote wipe capability

IT performs quarterly device compliance audits. Non-compliant devices may be temporarily restricted from network access until brought into compliance.

### Personal Devices (BYOD)

Personal devices may be used to access company email and Slack only if:
- The device runs a supported OS version (iOS 16+, Android 13+, macOS 13+, Windows 11+)
- A passcode/biometric lock is enabled
- The Meridian MDM profile is installed (lightweight — manages only company app data, not personal data)
- The device has not been jailbroken or rooted

Personal devices may NOT be used to access source code repositories, customer databases, production infrastructure, or any system containing PII or PHI.

## Data Classification and Handling

### Classification Levels

| Level | Description | Examples | Handling |
|-------|-------------|----------|----------|
| **Public** | Information approved for external sharing | Marketing materials, blog posts, published docs | No restrictions |
| **Internal** | General company information | Meeting notes, internal wikis, org charts | Share within company only |
| **Confidential** | Sensitive business data | Financial reports, product roadmaps, customer lists | Need-to-know basis, encrypted in transit and at rest |
| **Restricted** | Highest sensitivity | PII, PHI, payment data, credentials, security audit results | Strict access control, audit logging, encryption required |

### Data Handling Rules

- Never store Confidential or Restricted data on personal devices or personal cloud storage (Google Drive personal accounts, Dropbox, etc.)
- Never share Restricted data via email without encryption. Use the company's encrypted file sharing portal at secure.meridiantech.com
- Customer data must never be used in non-production environments unless anonymized. Contact the Data Engineering team for anonymized test datasets.
- All data transfers to third parties require a signed Data Processing Agreement (DPA) reviewed by Legal

### Data Retention

- Customer data: Retained for the duration of the customer contract plus 90 days
- Employee records: Retained for 7 years after termination per legal requirements
- System logs: Retained for 1 year (security logs for 2 years)
- Marketing analytics: Retained for 3 years

## Network Security

### VPN Usage

The company VPN (Tailscale) must be active when accessing internal tools from outside the office network. This includes:
- Internal dashboards and admin panels
- Source code repositories
- Customer databases
- CI/CD pipelines

The VPN is NOT required for: Google Workspace apps, Slack, Zoom, or the Meridian Analytics Platform (MAP) web interface.

### Wi-Fi Security

- Corporate Wi-Fi (MeridianSecure) uses WPA3 Enterprise with certificate-based authentication
- Guest Wi-Fi (MeridianGuest) is isolated from the corporate network and intended for visitors only
- Employees should never connect to MeridianGuest with company devices
- When working from public locations (cafes, airports), always use the VPN — even for non-sensitive browsing

## Incident Reporting

### What to Report

Report any suspected security incident immediately, including:
- Phishing emails or suspicious messages (forward to phishing@meridiantech.com)
- Lost or stolen devices
- Unauthorized access to accounts or systems
- Accidental data exposure (e.g., sending confidential data to the wrong recipient)
- Suspicious software or browser behavior
- Physical security concerns (tailgating, unlocked server rooms)

### How to Report

1. **Urgent incidents** (active breach, stolen device with sensitive data): Call the Security Hotline at (555) 867-5309, available 24/7
2. **Non-urgent incidents**: Submit a ticket at helpdesk.meridiantech.com under "Security Incident" or message #security-incidents on Slack

### Response Timeline

- **Critical** (active breach, ransomware): Response within 1 hour, containment within 4 hours
- **High** (stolen device, phishing compromise): Response within 4 hours
- **Medium** (suspicious activity, policy violation): Response within 24 hours
- **Low** (phishing report, security question): Response within 48 hours

## Software and Access

### Approved Software

Only IT-approved software may be installed on company devices. The approved software catalog is available at wiki.meridiantech.com/approved-software. To request new software, submit an IT ticket with the business justification.

Installing unapproved software, browser extensions (beyond those on the approved list), or connecting unapproved hardware may result in device quarantine and disciplinary action.

### Access Reviews

Access to systems and data is granted on a least-privilege basis. Managers review team access permissions quarterly. When employees change roles or departments, their access is re-evaluated within 5 business days. Access for departing employees is revoked within 2 hours of their exit time.

## Compliance and Consequences

Violations of this policy may result in:
- First offense: Written warning and mandatory security re-training
- Second offense: Suspension of system access pending review
- Severe or repeated violations: Termination of employment

All employees must complete annual Security Awareness Training and acknowledge this policy in Workday by January 31 each year.
