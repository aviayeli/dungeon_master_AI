from __future__ import annotations
import json
import urllib.parse
import urllib.request

WEB_SEARCH_TOOL: dict = {
    "name": "web_search",
    "description": (
        "Search the web for real-time information about D&D rules, "
        "monsters, spells, lore, or any other game-related facts."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query in Hebrew or English.",
            }
        },
        "required": ["query"],
    },
}


def execute_web_search(query: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        abstract = data.get("AbstractText", "")
        if abstract:
            return abstract[:600]
        related = data.get("RelatedTopics", [])
        snippets = [t["Text"] for t in related[:3] if isinstance(t, dict) and t.get("Text")]
        return "\n".join(snippets) if snippets else "לא נמצאו תוצאות רלוונטיות."
    except Exception as exc:
        return f"שגיאה בחיפוש: {exc}"


def handle_tool_call(name: str, inputs: dict) -> str:
    if name == "web_search":
        return execute_web_search(inputs.get("query", ""))
    return f"כלי לא מוכר: {name}"
