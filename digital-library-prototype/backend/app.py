
from flask import Flask, request, jsonify
from difflib import SequenceMatcher, get_close_matches
import json, os, re
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATA_PATH = os.path.join(os.path.dirname(__file__), "sample_data.json")

def load_data():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_data(items):
    with open(DATA_PATH, "w") as f:
        json.dump(items, f, indent=2)

def normalize(s):
    return (s or "").strip().lower()

def token_set(text):
    return set(re.findall(r"[a-z0-9]+", normalize(text)))

def boolean_parse(query):
    q = query.strip()
    if not q:
        return None
    phrases = re.findall(r'"([^"]+)"', q)
    for i, ph in enumerate(phrases):
        q = q.replace(f'"{ph}"', f'__PHRASE_{i}__')
    expr = []
    for tok in re.findall(r'\(|\)|\bAND\b|\bOR\b|\bNOT\b|[^\s()]+', q):
        if tok in ("AND", "OR", "NOT", "(", ")"):
            expr.append(tok.lower())
        elif tok.startswith("__PHRASE_"):
            idx = int(tok.split("_")[2])
            phrase = phrases[idx]
            expr.append(f'contains_phrase("{phrase}")')
        else:
            t = tok
            expr.append(f'contains_token("{t}")')
    py_expr = " ".join(expr).replace("and", " and ").replace("or", " or ").replace("not", " not ")

    def matcher(text):
        tokens = token_set(text)
        nt = normalize(text)

        def contains_token(t):
            return normalize(t) in tokens

        def contains_phrase(p):
            return normalize(p) in nt

        try:
            return eval(py_expr, {"__builtins__": {}}, {"contains_token": contains_token, "contains_phrase": contains_phrase})
        except Exception:
            return False

    return matcher

def score_item(item, query):
    ntq = normalize(query)
    if not ntq:
        return 0.0
    title = normalize(item.get("title", ""))
    author = normalize(item.get("author", ""))
    abstract = normalize(item.get("abstract", ""))
    text = " ".join([title, author, abstract])
    qtokens = token_set(ntq)
    itokens = token_set(text)
    overlap = len(qtokens & itokens)
    fuzz = max(SequenceMatcher(None, ntq, title).ratio(), SequenceMatcher(None, ntq, author).ratio())
    return overlap * 2.0 + fuzz

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/items")
def list_items():
    items = load_data()
    return jsonify(items)

@app.post("/api/items")
def add_item():
    items = load_data()
    new_item = request.get_json(force=True, silent=True) or {}
    new_item.setdefault("id", f"it-{len(items)+1:03d}")
    for k in ["title", "author", "isbn", "domain", "type", "year", "abstract", "keywords", "url"]:
        new_item.setdefault(k, "" if k != "year" and k != "keywords" else (0 if k=="year" else []))
    items.append(new_item)
    save_data(items)
    return jsonify({"ok": True, "id": new_item["id"]}), 201

@app.post("/api/search")
def search():
    payload = request.get_json(force=True, silent=True) or {}
    query = payload.get("q", "") or ""
    filters = payload.get("filters", {})
    mode = payload.get("mode", "keyword")

    items = load_data()

    def passes_filters(it):
        if filters.get("domain") and normalize(filters["domain"]) != normalize(it.get("domain", "")):
            return False
        if filters.get("type") and normalize(filters["type"]) != normalize(it.get("type", "")):
            return False
        if filters.get("author") and normalize(filters["author"]) not in normalize(it.get("author", "")):
            return False
        if filters.get("isbn") and normalize(filters["isbn"]) != normalize(it.get("isbn", "")):
            return False
        y_min = filters.get("year_min")
        y_max = filters.get("year_max")
        if y_min and int(it.get("year", 0)) < int(y_min):
            return False
        if y_max and int(it.get("year", 9999)) > int(y_max):
            return False
        return True

    pool = [it for it in items if passes_filters(it)]

    results = []
    if not query:
        results = sorted(pool, key=lambda x: x.get("year", 0), reverse=True)
    else:
        if mode == "boolean":
            matcher = boolean_parse(query)
            for it in pool:
                text = " ".join([it.get("title",""), it.get("author",""), it.get("abstract"," "), " ".join(it.get("keywords", []))])
                if matcher and matcher(text):
                    results.append((it, score_item(it, query)))
        elif mode == "fuzzy":
            choices = [it.get("title","") + " " + it.get("author","") for it in pool]
            close = get_close_matches(query, choices, n=min(20, len(choices)), cutoff=0.4)
            for it in pool:
                if any((it.get("title","") + " " + it.get("author","")).startswith(c) or c in (it.get("title","") + " " + it.get("author","")) for c in close):
                    results.append((it, score_item(it, query)))
            if not results:
                for it in pool:
                    results.append((it, score_item(it, query)))
        else:
            qtokens = token_set(query)
            for it in pool:
                text = " ".join([it.get("title",""), it.get("author",""), it.get("abstract",""), it.get("isbn",""), " ".join(it.get("keywords", []))])
                itokens = token_set(text)
                if qtokens & itokens:
                    results.append((it, score_item(it, query)))

        results.sort(key=lambda x: x[1], reverse=True)
        results = [it for it, _ in results]

    facets = {
        "domain": {},
        "type": {},
        "year": {}
    }
    for it in pool:
        facets["domain"][it.get("domain","")] = facets["domain"].get(it.get("domain",""), 0) + 1
        facets["type"][it.get("type","")] = facets["type"].get(it.get("type",""), 0) + 1
        facets["year"][str(it.get("year",""))] = facets["year"].get(str(it.get("year","")), 0) + 1

    return jsonify({
        "count": len(results),
        "results": results[:50],
        "facets": facets
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
