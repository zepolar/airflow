<!--
PR Title format: <type>: <short summary>
Examples: "feat: add model registry sync", "fix: handle empty dataset in ingest"
-->

### Summary
Provide a clear, concise summary of the changes. Why are they needed?

### Related Issues/Tickets
Link to related issues or tickets. Use keywords to auto-close if applicable.
Example: Closes #123

### Type of change
- [ ] feat (new feature)
- [ ] fix (bug fix)
- [ ] refactor (no functional changes)
- [ ] docs (documentation only)
- [ ] chore (build, tooling, dependencies)
- [ ] ci (CI/CD changes)

### What changed
- Bullet the key changes in this PR
- Keep it focused and scoped

### How to test
Describe the test plan so reviewers can verify the changes.
- [ ] Unit tests added/updated
- [ ] Manual steps to validate (commands, endpoints, expected output)

### Screenshots/Logs (optional)
Add images or relevant logs when helpful.

### Backward compatibility / Breaking changes
- Does this change break existing behavior or contracts? If yes, explain the migration path.

### Security & Compliance
- Data exposure/PII risk: [none/low/medium/high]
- Secrets/credentials touched: [yes/no] (explain if yes)
- New external services/dependencies: [yes/no]

### Checklist
- [ ] Code builds locally and CI checks pass
- [ ] Tests cover critical paths and edge cases
- [ ] Documentation updated (README/CHANGELOG/configs as needed)
- [ ] Naming, logging, and error handling follow project conventions
- [ ] If applicable, Airflow DAGs load and are idempotent

---
Note for this repository:
- Branch protection should enforce "Require review from Code Owners". With `.github/CODEOWNERS` set to `@zepolar`, only the repository owner will be able to approve PRs.
