# Security Policy

Report vulnerabilities privately through GitHub's security-advisory feature for this repository. Do not include credentials, private source code, access tokens, or exploitable customer data in a public issue.

These plugins can interact with local Git worktrees and GitHub pull requests. Review their authorization boundaries before use. In particular, the delivery plugin must receive explicit authorization before editing, committing, pushing, or commenting, and neither plugin authorizes merges, approvals, force pushes, destructive branch operations, or secret disclosure.
