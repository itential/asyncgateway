# Security Policy

## Supported Versions

Security fixes are applied to the latest release only. Older versions do not
receive backported security patches.

| Version | Supported |
|---------|-----------|
| latest  | Yes       |
| older   | No        |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities using one of these channels:

- **GitHub private disclosure (preferred):** Use
  [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)
  on the repository's Security tab.
- **Email:** Send details to [opensource@itential.com](mailto:opensource@itential.com)
  with the subject line `[SECURITY] asyncgateway <brief description>`.

## What to Include

A useful report includes:

- Description of the vulnerability and its potential impact
- Steps to reproduce or a minimal proof-of-concept
- Affected versions (if known)
- Suggested fix or mitigation (if you have one)

## Response Timeline

| Milestone | Target |
|-----------|--------|
| Acknowledgement | 3 business days |
| Initial assessment | 7 business days |
| Fix or mitigation | Depends on severity |
| Public disclosure | Coordinated with reporter |

Critical and high severity issues are prioritized. We will keep you informed
of progress and coordinate the disclosure timeline with you.

## Scope

**In scope:**

- Vulnerabilities in `asyncgateway` library code (`src/asyncgateway/`)
- Insecure defaults in the client or service layer
- Credential or secret exposure through logs or exceptions

**Out of scope:**

- Vulnerabilities in the upstream `ipsdk` dependency — report those directly
  to Itential
- Issues requiring physical access to the host system
- Vulnerabilities in development tooling (`ruff`, `pytest`, `bandit`, etc.)
- Social engineering

## Disclosure Policy

We follow coordinated disclosure. Once a fix is released, a GitHub Security
Advisory will be published. Credit is given to reporters unless anonymity is
requested.
