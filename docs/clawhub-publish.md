# ClawHub Publish Notes

## Skill

- slug: `open-feed-recsys-lab`
- name: `Open Feed Recsys Lab`
- version: `1.0.1`
- tags: `recsys,x-algorithm,phoenix,codex`
- source path: `skill/open-feed-recsys-lab`

## Publish Command

```bash
clawhub publish skill/open-feed-recsys-lab \
  --slug open-feed-recsys-lab \
  --name "Open Feed Recsys Lab" \
  --version 1.0.1 \
  --tags "recsys,x-algorithm,phoenix,codex" \
  --changelog "Align public license metadata with ClawHub MIT-0 registry display after the initial release."
```

## Expected Static Review Notes

The bundled script uses `subprocess` to run local `git` and optional `uv` commands. It also uses `urllib.request` for optional GitHub metadata. These are intentional and should be described as local reproducibility operations, not account-control or credential-handling behavior.

The skill does not ask for cookies, tokens, credentials, private X data, account analytics, or private messages.
