# Security Policy

## Reporting a Vulnerability

If you find a security vulnerability, please report it responsibly:

1. **Do NOT open a public issue**
2. **Use GitHub's [private vulnerability reporting](https://github.com/file-bricks/WinStorePackager/security/advisories/new)**
3. Include: description, steps to reproduce, potential impact

### How to Report

1. Go to: https://github.com/file-bricks/WinStorePackager/security/advisories/new
2. Fill out the form (title, description, severity, affected versions)
3. Submit privately (not visible to public until disclosed)

We will respond as soon as possible.

## Scope

- MSIX packaging
- Manifest generation
- Keyring credentials
- Host-local runtime settings and logs

## Local secrets and machine data

Certificate passwords are stored only through the operating-system Keyring. Publisher IDs,
certificate paths, SDK paths, settings, and logs are kept outside the source checkout under
the host-local runtime directory. A legacy checkout-local settings file is migrated only
after JSON validation and atomic readback; existing runtime settings are never overwritten.

## Response

As a solo project, response times may vary. Critical issues will be
prioritized. Please allow reasonable time before public disclosure.
