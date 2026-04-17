# Private Capture Helper (V1)

This is a lightweight, **no-extension** workflow for quickly capturing premium/private intel from pages you already have access to in your own logged-in browser session.

## Guardrails

- Do not bypass paywalls or auth.
- Only capture from content you are authorized to view.
- Keep captured quotes short and operational.

## One-click helper (bookmarklet)

Create a bookmark in your browser and set its URL to the snippet below:

```javascript
javascript:(() => {
  const selected = (window.getSelection && String(window.getSelection())) || "";
  const payload = {
    captured_at: new Date().toISOString(),
    source: prompt("Source label (ex: On3 premium board)", "") || "",
    page_title: document.title || "",
    url: location.href || "",
    selected_text: selected.trim(),
    quick_summary: prompt("Quick summary (optional)", "") || "",
    team_tags: (prompt("Team tags (comma-separated)", "") || "").split(",").map(v => v.trim()).filter(Boolean),
    player_tags: (prompt("Player tags (comma-separated)", "") || "").split(",").map(v => v.trim()).filter(Boolean),
    urgency: prompt("Urgency (low|medium|high)", "medium") || "medium",
    confidence: prompt("Confidence (low|medium|high or 0-1)", "medium") || "medium",
    note_type: prompt("Note type", "other") || "other"
  };

  const text = JSON.stringify(payload, null, 2);
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(text).then(() => alert("Capture copied to clipboard."));
  } else {
    prompt("Copy this capture JSON:", text);
  }
})();
```

## Local intake format

Use `data/private_capture_template.json` as the default structure for manual paste/edit.

- Single capture: one JSON object.
- Batch capture: JSON array of those objects.

## Convert capture into `private_intel.json`

### 1) Preview normalized output

```bash
python -m app.feedback.private_capture --input data/private_capture_template.json --print-only
```

### 2) Append into private intel store

```bash
python -m app.feedback.private_capture --input data/private_capture_template.json --output data/private_intel.json
```

## Field mapping

Capture helper fields map into engine schema as:

- `source` -> `source`
- `url` -> `article_url`
- `page_title` -> `title` (fallback to selected text snippet)
- `selected_text` + `quick_summary` -> `summary`
- `team_tags` -> `team_tags`
- `player_tags` -> `player_tags`
- `urgency` -> `urgency`
- `confidence` -> `confidence`
- `note_type` -> `note_type`

## Safe append workflow

1. Capture with bookmarklet while on the source page.
2. Paste JSON into `data/private_capture_template.json`.
3. Run `--print-only` and sanity-check fields.
4. Run append command.
5. Optionally re-open `data/private_intel.json` and confirm the new entry is at the end.

This keeps intake fast for creators/operators while preserving the existing private intel schema.
