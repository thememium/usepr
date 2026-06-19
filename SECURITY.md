# Reporting a Vulnerability

To report a security vulnerability, please email boswell.labs@gmail.com.

We take security seriously and will respond to security reports within 48 hours. Please include as much detail as possible about the vulnerability, including:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

While the discovery of new vulnerabilities is rare, we also recommend always using the latest version of usePR to ensure your application remains as secure as possible.

## Security Considerations for usePR

As usePR is a CLI tool that generates PR summaries using AI, please be aware of the following security practices:

- **API Keys**: usePR requires API keys for LLM providers (OpenAI, Anthropic, etc.). Never commit these keys to version control. Use environment variables to store them securely.
- **Git Repository Access**: usePR reads your git history and diff data. Ensure you trust the repository you're running it in.

## Security Hall of Fame

We would like to thank the following security researchers for responsibly disclosing security issues to us.

*No security researchers have been added to the hall of fame yet. Will you be the first?*
