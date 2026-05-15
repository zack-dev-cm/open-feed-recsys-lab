# ClawHub Publish Notes

## Skill

- slug: `open-feed-recsys-lab`
- name: `Open Feed Recsys Lab`
- version: `1.0.0`
- tags: `recsys,x-algorithm,phoenix,codex`
- source path: `skill/open-feed-recsys-lab`

## Publish Command

```bash
clawhub publish skill/open-feed-recsys-lab \
  --slug open-feed-recsys-lab \
  --name "Open Feed Recsys Lab" \
  --version 1.0.0 \
  --tags "recsys,x-algorithm,phoenix,codex" \
  --changelog "Initial public release for commit-pinned reports, Phoenix artifact checks, documentation mismatch detection, and architecture maps for open feed recommendation repos."
```

## Expected Static Review Notes

The bundled script uses `subprocess` to run local `git` and optional `uv` commands. It also uses `urllib.request` for optional GitHub metadata. These are intentional and should be described as local reproducibility operations, not account-control or credential-handling behavior.

The skill does not ask for cookies, tokens, credentials, private X data, account analytics, or private messages.
