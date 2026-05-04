# Security Policy

## 1. Security Philosophy

SecureCleaner is designed with a **Zero-Trust** approach to local file manipulation. We prioritize data integrity and non-repudiation.

## 2. Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

## 3. Implemented Protections

- **Principle of Least Privilege (PoLP):** Hardcoded restrictions prevent the kernel from accessing `C:\Windows`, `Program Files`, and other root system directories.
- **Brute-Force Protection:** A linear backoff and 60-second hardware lockout are triggered after 3 failed administrative attempts.
- **Atomic Auditing:** Utilizing `os.fsync()`, all security events are flushed directly to physical storage to prevent log-tampering during process termination.

## 4. Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report vulnerabilities by following these steps:

1. Email the maintainer at [YOUR_EMAIL@HERE.com].
2. Include a detailed description of the exploit and a Proof of Concept (PoC).
3. A response will be provided within 48 hours.

## 5. Disclosure Process

We follow a **90-day responsible disclosure** timeline. We will coordinate with the reporter to release a fix before the vulnerability is made public to protect our users.
