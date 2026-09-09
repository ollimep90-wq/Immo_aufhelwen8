# Obsidian Local REST API (optional, later stage)

**Default path is the filesystem.** Obsidian watches the vault directory and picks
up external changes within a second, so writing `.md` files directly works while
the app is running. Use the REST API only when you actually need something the
filesystem cannot give you:

- the vault lives on a machine you can only reach over the network
- you need the **currently open note** (`/active/`)
- you want Obsidian's own index: Dataview DQL executed by Obsidian, or its search
- you want to trigger an Obsidian command

One filesystem caveat: **do not rewrite a file the user has open with unsaved
changes** — Obsidian will save over your version. If in doubt, ask them to close
or save the note first.

## Setup

1. Obsidian → Settings → Community plugins → Browse → **Local REST API**
   (by coddingtonbear) → Install → Enable.
2. Copy the **API key** from the plugin settings.
3. Ports: HTTPS **27124** (default, self-signed certificate) and optionally
   HTTP **27123** (must be switched on explicitly; only ever bind it to
   `127.0.0.1`).
4. The plugin settings page offers the certificate for download — trust that,
   rather than turning verification off permanently.

Store the key **outside the vault and outside the repo**, e.g. in
`~/.config/claude-obsidian/rest.env` with mode `600`:

```
OBSIDIAN_API_KEY=…
OBSIDIAN_API_URL=https://127.0.0.1:27124
```

The key grants full read/write on the whole vault. It must never end up in a note,
a commit, a log or a shell history file. Use `set -a; . ~/.config/claude-obsidian/rest.env; set +a`.

## Endpoints (as of plugin v3.x)

Authentication: `Authorization: Bearer $OBSIDIAN_API_KEY` on every request.
Paths are **vault-relative** and must be URL-encoded.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | status / whether auth works |
| `GET` | `/vault/{path}` | read a note (`Accept: application/vnd.olrapi.note+json` gives frontmatter and tags parsed) |
| `PUT` | `/vault/{path}` | create or **replace** a note |
| `POST` | `/vault/{path}` | append to a note |
| `PATCH` | `/vault/{path}` | insert relative to a heading, block ref or frontmatter field |
| `DELETE` | `/vault/{path}` | delete a note |
| `GET` | `/vault/{dir}/` | list a directory (trailing slash) |
| `GET`/`PUT`/`POST`/`PATCH` | `/active/` | the note currently open |
| `POST` | `/search/simple/?query=…` | plain text search |
| `POST` | `/search/` | Dataview DQL (`Content-Type: application/vnd.olrapi.dataview.dql+txt`) or JsonLogic |
| `GET` | `/commands/` · `POST /commands/{id}` | list / execute an Obsidian command |
| `GET` | `/open/{path}` | open a note in the UI |
| `GET` | `/openapi.yaml` | the full, authoritative spec |

When anything below disagrees with `/openapi.yaml`, the spec wins — check it
before debugging.

## Examples

```bash
set -a; . ~/.config/claude-obsidian/rest.env; set +a
AUTH="Authorization: Bearer $OBSIDIAN_API_KEY"

# reachable?
curl -sS --cacert ~/.config/claude-obsidian/obsidian-local-rest-api.crt \
     -H "$AUTH" "$OBSIDIAN_API_URL/"

# read a property note with parsed frontmatter
curl -sS -H "$AUTH" -H "Accept: application/vnd.olrapi.note+json" \
     "$OBSIDIAN_API_URL/vault/10-Objekte/OBJ-2026-001/OBJ-2026-001.md" | jq .frontmatter

# append to the Verlauf section (append, never replace)
curl -sS -X POST -H "$AUTH" -H "Content-Type: text/markdown" \
     --data-binary $'\n- 2026-03-14: Teilungserklärung erhalten.' \
     "$OBSIDIAN_API_URL/vault/10-Objekte/OBJ-2026-001/OBJ-2026-001.md"

# run a Dataview query through Obsidian's own index
curl -sS -X POST -H "$AUTH" \
     -H "Content-Type: application/vnd.olrapi.dataview.dql+txt" \
     --data-binary 'TABLE price_asking FROM "10-Objekte" WHERE type = "objekt"' \
     "$OBSIDIAN_API_URL/search/"
```

`--insecure` works against the self-signed certificate but is a bad habit — prefer
`--cacert` with the downloaded certificate.

## Rules when using the API

- **`PUT` replaces the whole note.** Read first, edit, write back — or use `PATCH`
  / `POST` for additions. A careless `PUT` silently destroys the user's prose.
- Obsidian must be running and unlocked; there is no API on mobile.
- Failures are silent in the UI. Check the HTTP status of every write.
- Nothing in this file changes the rules in `SKILL.md`: sources, no invented
  numbers, calculations through the script.
