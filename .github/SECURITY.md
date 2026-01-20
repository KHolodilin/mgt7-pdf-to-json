# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for
receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities by creating a [security advisory](https://github.com/KHolodilin/mgt7-pdf-to-json/security/advisories/new) on GitHub. You will receive a response within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible vulnerability:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

## Security Best Practices

When using this project, please follow these security best practices:

1. **Keep dependencies up to date**: Regularly update all dependencies to their latest secure versions
2. **Validate input files**: Always validate PDF files before processing
3. **Use secure file handling**: Ensure proper file permissions and avoid processing files from untrusted sources
4. **Monitor logs**: Review logs regularly for suspicious activity
5. **Limit access**: Restrict access to sensitive data and artifacts

## Known Security Considerations

- **PDF Processing**: This tool processes PDF files which may contain malicious content. Always validate and sanitize input files.
- **File System Access**: The tool creates temporary files and artifacts. Ensure proper file system permissions.
- **Dependencies**: We regularly audit dependencies for known vulnerabilities using tools like `safety` and `bandit`.

## Disclosure Policy

When we receive a security bug report, we will assign it to a primary handler. This person will coordinate the fix and release process, involving the following steps:

1. Confirm the problem and determine the affected versions.
2. Audit code to find any potential similar problems.
3. Prepare fixes for all releases still in maintenance. These fixes will be released as fast as possible to the public.

## Recognition

We recognize security researchers who responsibly disclose vulnerabilities. If you would like to be credited, please let us know how you would like to be recognized (name, handle, organization, etc.).
