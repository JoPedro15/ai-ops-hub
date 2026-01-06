# 🌿 Git & Workflow Conventions

To ensure absolute traceability and maintain a professional history in the **AI-Ops Hub**, all contributors must follow these standardized rules.

## 🌿 Branch Naming Strategy

Format: `<type>/<short-description>` (Use hyphens for spaces).

| Type        | Use Case                                           |
| :---------- | :------------------------------------------------- |
| `feat/`     | New features or major capabilities.                |
| `infra/`    | Changes to core services (gdrive, ai_utils, etc.). |
| `bug/`      | Fixes and patches.                                 |
| `maint/`    | Documentation, CI/CD, and repository maintenance.  |
| `research/` | Jupyter Notebooks and AI experiments in `/lab`.    |

## 💬 Commit Messages (The 50/72 Rule)

We use descriptive titles in **English**. If an issue exists, link it at the end.

**Format**: `<type>: <description>`

- **Good**: `feat: add exponential backoff to gdrive uploader`
- **Good**: `infra: fix circular import in ai_utils ingestor (closes #42)`
- **Bad**: `fixed stuff` or `update files`

### Guidelines:

- Use the **imperative mood** ("add", not "added" or "adds").
- Keep the subject line under **50 characters**.
- Capitalize the subject line only if necessary (standard is lowercase after the prefix).

## 💎 The Quality Gate (Pre-Push)

Before pushing any branch or opening a Pull Request (PR), you must ensure the code passes the local quality suite. **A failed suite means a "No Rep".**

```bash
# Executed from the project roots
make quality
```

______________________________________________________________________

João Pedro | Automation Engineer <br /> [GitHub profile](https://github.com/JoPedro15)
