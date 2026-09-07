# Security Policy

## Supported version

Security fixes are applied to the latest version on the default branch.

## Reporting

Please use GitHub's private vulnerability reporting feature instead of opening a public issue with exploit details.

## Security boundaries

- Secrets and environment-specific database paths are supplied at runtime.
- Browser writes require CSRF validation.
- SQL statements use parameters; persisted values are constrained by the schema.
- Comments are trimmed, required, and limited to 1,000 characters.
- The API performs no file upload, shell execution, or external request.
- Flask auto-escaping remains enabled for user content.

For production, set a strong random `SECRET_KEY`, terminate TLS at a trusted proxy, configure secure cookies, add abuse controls, and use a production WSGI server.
