"""
ui_web.py  -  Graphical Web UI for the Financial IR System (CS 5180)
Depends on: search_engine.py, text_processing.py

Install:  pip install flask
Run:      python3 ui_web.py
Open:     http://localhost:5000

File layout expected:
    dataset/documents.json
    dataset/queries.json
    dataset/qrels.json
    outputs/tokenized_documents.json
"""

import json
import os
import sys

from flask import Flask, render_template_string, request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from search_engine import FinancialIR

# ── constants ──────────────────────────────────────────────────────────────────
TOKENIZED_DOCS = "outputs/tokenized_documents.json"
RAW_DOCS       = "dataset/documents.json"
QUERIES_PATH   = "dataset/queries.json"
QRELS_PATH     = "dataset/qrels.json"
PAGE_SIZE      = 5
TOP_N          = 25

# ── load IR engine ─────────────────────────────────────────────────────────────
print("Loading IR engine...", end="", flush=True)
ir = FinancialIR(TOKENIZED_DOCS, RAW_DOCS)
print(f" done ({len(ir.doc_ids):,} documents indexed)")

app = Flask(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# BASE HTML (shared layout)
# ══════════════════════════════════════════════════════════════════════════════
BASE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Financial IR · CS 5180</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#06080f;
  --s1:#0d1117;
  --s2:#161b27;
  --border:#1f2937;
  --gold:#3b82f6;
  --gold2:#60a5fa;
  --green:#34d399;
  --blue:#60a5fa;
  --red:#f87171;
  --text:#e2e8f0;
  --muted:#64748b;
  --r:6px;
}
body{
  background:var(--bg);color:var(--text);
  font-family:'DM Sans',sans-serif;font-weight:300;
  min-height:100vh;
  background-image:radial-gradient(ellipse 70% 40% at 50% 0%,rgba(59,130,246,.08) 0%,transparent 60%);
}
a{text-decoration:none;color:inherit}
nav{
  display:flex;align-items:center;justify-content:space-between;
  padding:.9rem 2rem;border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:99;
  background:rgba(6,8,15,.9);backdrop-filter:blur(12px);
}
.logo{font-family:'DM Serif Display',serif;font-size:1.35rem;color:var(--gold)}
.logo span{color:var(--text)}
.nav-links{display:flex;gap:.25rem}
.nav-links a{
  padding:.4rem .85rem;border-radius:var(--r);
  font-size:.82rem;font-weight:500;color:var(--muted);transition:all .15s;
}
.nav-links a:hover{color:var(--text);background:var(--s2)}
.nav-links a.active{color:var(--gold);background:rgba(59,130,246,.1)}
.page{max-width:860px;margin:0 auto;padding:2rem 1.5rem 4rem}
.hero{text-align:center;padding:3.5rem 1rem 2.5rem}
.hero h1{
  font-family:'DM Serif Display',serif;
  font-size:clamp(2rem,5vw,3.2rem);
  color:var(--gold);line-height:1.1;margin-bottom:.5rem;
}
.hero p{color:var(--muted);font-size:.9rem;letter-spacing:.04em;text-transform:uppercase}
.search-wrap{max-width:620px;margin:2rem auto 0}
.search-box{
  display:flex;background:var(--s2);border:1px solid var(--border);
  border-radius:50px;overflow:hidden;
  box-shadow:0 0 0 0 rgba(59,130,246,0);transition:box-shadow .2s,border-color .2s;
}
.search-box:focus-within{
  border-color:rgba(59,130,246,.5);box-shadow:0 0 0 3px rgba(59,130,246,.08);
}
.search-box input{
  flex:1;padding:.85rem 1.4rem;
  background:transparent;border:none;outline:none;
  color:var(--text);font-family:'DM Sans',sans-serif;font-size:.93rem;
}
.search-box input::placeholder{color:var(--muted)}
.search-box button{
  padding:.85rem 1.6rem;background:var(--gold);color:#fff;border:none;
  font-weight:600;font-size:.82rem;letter-spacing:.06em;text-transform:uppercase;
  cursor:pointer;border-radius:0 50px 50px 0;transition:background .15s;
}
.search-box button:hover{background:var(--gold2)}
.info-bar{
  display:flex;align-items:center;gap:1rem;flex-wrap:wrap;
  padding:.55rem 1rem;margin-bottom:1.2rem;
  background:var(--s1);border:1px solid var(--border);border-radius:var(--r);
  font-size:.8rem;color:var(--muted);
}
.info-bar strong{color:var(--text)}
.card{
  background:var(--s1);border:1px solid var(--border);
  border-radius:var(--r);padding:1.1rem 1.3rem;margin-bottom:.75rem;
  transition:border-color .15s,box-shadow .15s;
  animation:rise .3s ease both;
}
.card:hover{border-color:rgba(59,130,246,.35);box-shadow:0 4px 20px rgba(0,0,0,.4)}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.card-top{display:flex;align-items:center;gap:.75rem;margin-bottom:.75rem}
.rank-badge{
  width:1.9rem;height:1.9rem;border-radius:50%;
  background:var(--gold);color:#fff;
  display:grid;place-items:center;
  font-family:'JetBrains Mono',monospace;font-size:.7rem;font-weight:600;flex-shrink:0;
}
.doc-id{font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--blue)}
.score{
  margin-left:auto;background:rgba(52,211,153,.08);color:var(--green);
  border:1px solid rgba(52,211,153,.2);border-radius:20px;padding:.18rem .65rem;
  font-size:.72rem;font-family:'JetBrains Mono',monospace;
}
.card-text{
  font-size:.85rem;line-height:1.65;color:#94a3b8;
  overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;
}
.card-text.open{-webkit-line-clamp:unset}
.toggle-btn{
  background:none;border:none;color:var(--muted);font-size:.75rem;
  cursor:pointer;margin-top:.4rem;padding:0;transition:color .15s;
}
.toggle-btn:hover{color:var(--gold)}
.pager{display:flex;gap:.4rem;justify-content:center;margin-top:1.8rem;flex-wrap:wrap}
.pager a{
  padding:.4rem .85rem;border-radius:var(--r);
  background:var(--s2);border:1px solid var(--border);
  color:var(--text);font-size:.8rem;transition:all .15s;
}
.pager a:hover{border-color:var(--gold);color:var(--gold)}
.pager a.on{background:var(--gold);color:#fff;border-color:var(--gold);font-weight:600}
.pager a.off{opacity:.35;pointer-events:none}
.stitle{
  font-family:'DM Serif Display',serif;font-size:1.5rem;color:var(--gold);
  margin:0 0 1.2rem;padding-bottom:.6rem;border-bottom:1px solid var(--border);
}
.panel{
  background:var(--s1);border:1px solid var(--border);
  border-radius:var(--r);padding:1.4rem;margin-bottom:1.2rem;
}
.panel h2{font-family:'DM Serif Display',serif;font-size:1.1rem;color:var(--gold);margin-bottom:1rem}
.big-score{
  text-align:center;padding:1.5rem;
  font-family:'JetBrains Mono',monospace;font-size:2.8rem;color:var(--green);font-weight:600;
}
.big-label{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-top:.2rem}
table{width:100%;border-collapse:collapse;font-size:.82rem;margin-top:.8rem}
th{
  text-align:left;padding:.45rem .7rem;
  font-family:'JetBrains Mono',monospace;font-size:.68rem;
  text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
  border-bottom:1px solid var(--border);
}
td{padding:.5rem .7rem;border-bottom:1px solid rgba(255,255,255,.03)}
tr:hover td{background:rgba(255,255,255,.02)}
.ap-hi{color:var(--green)}.ap-mid{color:var(--gold)}.ap-lo{color:var(--red)}
.form-group{margin-bottom:.9rem}
.form-group label{
  display:block;font-size:.75rem;color:var(--muted);
  text-transform:uppercase;letter-spacing:.07em;margin-bottom:.3rem;
}
.form-group input[type=text],
.form-group textarea{
  width:100%;padding:.65rem .9rem;
  background:var(--s2);border:1px solid var(--border);border-radius:var(--r);
  color:var(--text);font-family:'DM Sans',sans-serif;font-size:.87rem;
  outline:none;transition:border-color .15s;
}
.form-group input[type=text]:focus,
.form-group textarea:focus{border-color:rgba(59,130,246,.5)}
.form-group textarea{resize:vertical;min-height:90px}
.btn{
  display:inline-block;padding:.65rem 1.4rem;
  background:var(--gold);color:#fff;border:none;border-radius:var(--r);
  font-weight:600;font-size:.82rem;letter-spacing:.04em;
  text-transform:uppercase;cursor:pointer;transition:background .15s;
}
.btn:hover{background:var(--gold2)}
.btn-outline{
  background:transparent;color:var(--text);border:1px solid var(--border);margin-left:.5rem;
}
.btn-outline:hover{border-color:var(--gold);color:var(--gold);background:transparent}
.alert{padding:.75rem 1rem;border-radius:var(--r);font-size:.84rem;margin-bottom:1rem}
.alert-ok{background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.25);color:var(--green)}
.alert-err{background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.25);color:var(--red)}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:.8rem;margin-top:1rem}
.stat-card{
  background:var(--s2);border:1px solid var(--border);border-radius:var(--r);padding:1rem;text-align:center;
}
.stat-val{font-family:'JetBrains Mono',monospace;font-size:1.5rem;color:var(--gold);font-weight:600}
.stat-lbl{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-top:.25rem}
code{
  font-family:'JetBrains Mono',monospace;font-size:.82em;
  background:var(--s2);padding:.1em .35em;border-radius:3px;
}
</style>
</head>
<body>
<nav>
  <div class="logo">Financial IR System</div>
  <div class="nav-links">
    <a href="/"         class="{{ 'active' if active_page=='search'   else '' }}">Search</a>
    <a href="/evaluate" class="{{ 'active' if active_page=='evaluate' else '' }}">Evaluate</a>
    <a href="/dynamic"  class="{{ 'active' if active_page=='dynamic'  else '' }}">Dynamic</a>
    <a href="/add"      class="{{ 'active' if active_page=='add'      else '' }}">Add Docs</a>
    <a href="/stats"    class="{{ 'active' if active_page=='stats'    else '' }}">Stats</a>
  </div>
</nav>
{% block content %}{% endblock %}
<script>
function toggle(id,btn){
  var el=document.getElementById(id);
  el.classList.toggle('open');
  btn.textContent=el.classList.contains('open')?'Show less \u25b2':'Show more \u25bc';
}
</script>
</body></html>"""


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════
SEARCH_TMPL = BASE.replace("{% block content %}{% endblock %}", """{% block content %}
<div class="hero">
  <h1>Financial Document Search</h1>
  <p>BM25 Information Retrieval · CS 5180</p>
  <div class="search-wrap">
    <form class="search-box" method="GET" action="/search">
      <input name="q" type="text" placeholder="e.g. stock market volatility…"
             value="{{ query|e }}" autocomplete="off" autofocus/>
      <button type="submit">Search</button>
    </form>
  </div>
</div>
{% endblock %}""")

RESULTS_TMPL = BASE.replace("{% block content %}{% endblock %}", """{% block content %}
<div class="hero" style="padding-bottom:1.5rem">
  <div class="search-wrap" style="margin-top:0">
    <form class="search-box" method="GET" action="/search">
      <input name="q" type="text" value="{{ query|e }}" autocomplete="off"/>
      <button type="submit">Search</button>
    </form>
  </div>
</div>
<div class="page">
  <div class="info-bar">
    <span>Query: <strong>{{ query|e }}</strong></span>
    <span style="color:var(--border)">|</span>
    <span>Showing <strong>{{ start+1 }}&ndash;{{ end }}</strong> of <strong>{{ total }}</strong></span>
    <span style="color:var(--border)">|</span>
    <span>Page <strong>{{ cur_page+1 }}</strong> / {{ total_pages }}</span>
  </div>
  {% for doc in page_docs %}
  <div class="card" style="animation-delay:{{ loop.index0 * 0.05 }}s">
    <div class="card-top">
      <div class="rank-badge">{{ start + loop.index }}</div>
      <span class="doc-id">{{ doc.doc_id }}</span>
      <span class="score">{{ "%.4f"|format(doc.score) }}</span>
    </div>
    <div class="card-text" id="t{{ loop.index0 }}">{{ doc.text }}</div>
    <button class="toggle-btn" onclick="toggle('t{{ loop.index0 }}',this)">Show more &#9660;</button>
  </div>
  {% endfor %}
  <div class="pager">
    <a class="{{ 'off' if cur_page==0 else '' }}"
       href="/search?q={{ query|urlencode }}&p={{ cur_page-1 }}">&larr; Prev</a>
    {% for i in range(total_pages) %}
      <a class="{{ 'on' if i==cur_page else '' }}"
         href="/search?q={{ query|urlencode }}&p={{ i }}">{{ i+1 }}</a>
    {% endfor %}
    <a class="{{ 'off' if cur_page>=total_pages-1 else '' }}"
       href="/search?q={{ query|urlencode }}&p={{ cur_page+1 }}">Next &rarr;</a>
  </div>
</div>
{% endblock %}""")


# ══════════════════════════════════════════════════════════════════════════════
# EVALUATE TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
EVAL_TMPL = BASE.replace("{% block content %}{% endblock %}", """{% block content %}
<div class="page">
  <div class="stitle">Static Evaluation &mdash; MAP / AP</div>
  {% if error %}<div class="alert alert-err">{{ error }}</div>{% endif %}
  {% if ran %}
    <div class="panel">
      <div class="big-score">{{ "%.4f"|format(map_score) }}
        <div class="big-label">Mean Average Precision (MAP)</div>
      </div>
      <table>
        <thead><tr><th>Query ID</th><th>Query Text</th><th>AP</th></tr></thead>
        <tbody>
        {% for r in rows %}
          <tr>
            <td><code>{{ r.qid }}</code></td>
            <td>{{ r.text[:70] }}{% if r.text|length > 70 %}&hellip;{% endif %}</td>
            <td class="{{ 'ap-hi' if r.ap>=0.5 else ('ap-mid' if r.ap>=0.2 else 'ap-lo') }}">
              {{ "%.4f"|format(r.ap) }}
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
    <form method="POST" action="/evaluate">
      <button class="btn" type="submit">Re-run</button>
    </form>
  {% else %}
    <div class="panel">
      <h2>Run Static Evaluation</h2>
      <p style="color:var(--muted);font-size:.86rem;margin-bottom:1.2rem">
        Uses <code>dataset/queries.json</code> and <code>dataset/qrels.json</code>.
        Computes AP per query and MAP across all 25 queries.
      </p>
      <form method="POST" action="/evaluate">
        <button class="btn" type="submit">Run Evaluation</button>
      </form>
    </div>
  {% endif %}
</div>
{% endblock %}""")


# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
DYNAMIC_TMPL = BASE.replace("{% block content %}{% endblock %}", """{% block content %}
<div class="page">
  <div class="stitle">Dynamic Labeled Query Evaluation</div>
  {% if error %}<div class="alert alert-err">{{ error }}</div>{% endif %}
  {% if ran %}
    <div class="panel">
      <div class="big-score">{{ "%.4f"|format(map_score) }}
        <div class="big-label">Mean Average Precision (MAP)</div>
      </div>
      <table>
        <thead><tr><th>Query</th><th>Relevant Docs</th><th>AP</th></tr></thead>
        <tbody>
        {% for r in rows %}
          <tr>
            <td>{{ r.text[:60] }}{% if r.text|length > 60 %}&hellip;{% endif %}</td>
            <td>{{ r.n_rel }}</td>
            <td class="{{ 'ap-hi' if r.ap>=0.5 else ('ap-mid' if r.ap>=0.2 else 'ap-lo') }}">
              {{ "%.4f"|format(r.ap) }}
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
    <a href="/dynamic" class="btn" style="display:inline-block;margin-top:.5rem">&larr; New Evaluation</a>
  {% else %}
    <div class="panel">
      <h2>Enter Queries</h2>
      <p style="color:var(--muted);font-size:.85rem;margin-bottom:1.2rem">
        Enter 2&ndash;3 queries with relevant doc IDs. Leave unused rows blank.
      </p>
      <form method="POST" action="/dynamic">
        {% for i in range(1,4) %}
        <div style="border:1px solid var(--border);border-radius:var(--r);padding:1rem;margin-bottom:.8rem">
          <p style="font-size:.78rem;color:var(--muted);margin-bottom:.7rem;text-transform:uppercase;letter-spacing:.06em">
            Query {{ i }}
          </p>
          <div class="form-group">
            <label>Query Text</label>
            <input type="text" name="qt{{ i }}" placeholder="e.g. portfolio risk management"/>
          </div>
          <div class="form-group">
            <label>Relevant Doc IDs (comma-separated)</label>
            <input type="text" name="rd{{ i }}" placeholder="e.g. 0042, 0187"/>
          </div>
        </div>
        {% endfor %}
        <button class="btn" type="submit">Run Evaluation</button>
      </form>
    </div>
  {% endif %}
</div>
{% endblock %}""")


# ══════════════════════════════════════════════════════════════════════════════
# ADD DOCS TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
ADD_TMPL = BASE.replace("{% block content %}{% endblock %}", """{% block content %}
<div class="page">
  <div class="stitle">Add Documents to Corpus</div>
  {% if success %}<div class="alert alert-ok">{{ success }}</div>{% endif %}
  {% if error %}<div class="alert alert-err">{{ error }}</div>{% endif %}
  <div class="panel">
    <h2>Manual Entry</h2>
    <form method="POST" action="/add">
      <div class="form-group">
        <label>Document ID</label>
        <input type="text" name="doc_id" placeholder="e.g. fin_5001" required/>
      </div>
      <div class="form-group">
        <label>Document Text</label>
        <textarea name="text" placeholder="Paste document text here&hellip;" required></textarea>
      </div>
      <button class="btn" type="submit">Add Document</button>
    </form>
  </div>
  <div class="panel">
    <h2>Bulk Upload via File Path</h2>
    <p style="color:var(--muted);font-size:.84rem;margin-bottom:1rem">
      Provide a path to a JSON file: <code>[{"doc_id":"...","text":"..."},&hellip;]</code>
    </p>
    <form method="POST" action="/add_bulk">
      <div class="form-group">
        <label>File Path</label>
        <input type="text" name="path" placeholder="e.g. dataset/new_docs.json"/>
      </div>
      <button class="btn" type="submit">Load &amp; Index</button>
    </form>
  </div>
</div>
{% endblock %}""")


# ══════════════════════════════════════════════════════════════════════════════
# STATS TEMPLATE
# ══════════════════════════════════════════════════════════════════════════════
STATS_TMPL = BASE.replace("{% block content %}{% endblock %}", """{% block content %}
<div class="page">
  <div class="stitle">Corpus Statistics</div>
  <div class="stat-grid">
    <div class="stat-card">
      <div class="stat-val">{{ total_docs }}</div>
      <div class="stat-lbl">Documents</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{{ vocab_size }}</div>
      <div class="stat-lbl">Vocabulary</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{{ avg_tokens }}</div>
      <div class="stat-lbl">Avg Tokens / Doc</div>
    </div>
  </div>
</div>
{% endblock %}""")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def home():
    return render_template_string(SEARCH_TMPL, active_page="search", query="")


@app.route("/search")
def search():
    query    = request.args.get("q", "").strip()
    cur_page = int(request.args.get("p", 0))

    if not query:
        return render_template_string(SEARCH_TMPL, active_page="search", query="")

    results     = ir.search(query, n=TOP_N)
    total       = len(results)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    cur_page    = max(0, min(cur_page, total_pages - 1))
    start       = cur_page * PAGE_SIZE
    end         = min(start + PAGE_SIZE, total)

    return render_template_string(
        RESULTS_TMPL,
        active_page="search",
        query=query,
        page_docs=results[start:end],
        start=start,
        end=end,
        total=total,
        cur_page=cur_page,
        total_pages=total_pages,
    )


@app.route("/evaluate", methods=["GET", "POST"])
def evaluate():
    if request.method == "GET":
        return render_template_string(EVAL_TMPL, active_page="evaluate", ran=False, error=None)

    if not os.path.exists(QUERIES_PATH):
        return render_template_string(EVAL_TMPL, active_page="evaluate", ran=False,
            error=f"File not found: {QUERIES_PATH}", rows=[], map_score=0)
    if not os.path.exists(QRELS_PATH):
        return render_template_string(EVAL_TMPL, active_page="evaluate", ran=False,
            error=f"File not found: {QRELS_PATH}", rows=[], map_score=0)

    with open(QUERIES_PATH, encoding="utf-8") as f:
        queries = json.load(f)
    with open(QRELS_PATH, encoding="utf-8") as f:
        qrels_raw = json.load(f)

    qrels = {}
    for e in qrels_raw:
        qrels.setdefault(e["query_id"], set()).add(e["doc_id"])

    rows      = []
    ap_scores = []
    for q in queries:
        qid  = q["query_id"]
        rels = qrels.get(qid, set())
        if not rels:
            continue
        results  = ir.search(q["text"], n=len(ir.doc_ids))
        hits = total_p = 0
        for rank, res in enumerate(results, 1):
            if res["doc_id"] in rels:
                hits += 1
                total_p += hits / rank
        ap = total_p / len(rels)
        ap_scores.append(ap)
        rows.append({"qid": qid, "text": q["text"], "ap": ap})

    map_score = sum(ap_scores) / len(ap_scores) if ap_scores else 0.0
    return render_template_string(EVAL_TMPL, active_page="evaluate",
        ran=True, map_score=map_score, rows=rows, error=None)


@app.route("/dynamic", methods=["GET", "POST"])
def dynamic():
    if request.method == "GET":
        return render_template_string(DYNAMIC_TMPL, active_page="dynamic", ran=False, error=None)

    queries_in = []
    for i in range(1, 4):
        text     = request.form.get(f"qt{i}", "").strip()
        rels_raw = request.form.get(f"rd{i}", "").strip()
        if text:
            rels = {d.strip() for d in rels_raw.split(",") if d.strip()}
            queries_in.append({"text": text, "rels": rels})

    if not queries_in:
        return render_template_string(DYNAMIC_TMPL, active_page="dynamic", ran=False,
            error="Please enter at least one query.")

    rows      = []
    ap_scores = []
    for q in queries_in:
        rels    = q["rels"]
        results = ir.search(q["text"], n=len(ir.doc_ids))
        hits = total_p = 0
        for rank, res in enumerate(results, 1):
            if res["doc_id"] in rels:
                hits += 1
                total_p += hits / rank
        ap = total_p / len(rels) if rels else 0.0
        ap_scores.append(ap)
        rows.append({"text": q["text"], "n_rel": len(rels), "ap": ap})

    map_score = sum(ap_scores) / len(ap_scores) if ap_scores else 0.0
    return render_template_string(DYNAMIC_TMPL, active_page="dynamic",
        ran=True, map_score=map_score, rows=rows, error=None)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return render_template_string(ADD_TMPL, active_page="add", success=None, error=None)
    doc_id = request.form.get("doc_id", "").strip()
    text   = request.form.get("text",   "").strip()
    if not doc_id or not text:
        return render_template_string(ADD_TMPL, active_page="add",
            error="Both Doc ID and Text are required.", success=None)
    ir.update_corpus([{"doc_id": doc_id, "text": text}])
    return render_template_string(ADD_TMPL, active_page="add",
        success=f"Document '{doc_id}' added. Corpus now has {len(ir.doc_ids):,} documents.",
        error=None)


@app.route("/add_bulk", methods=["POST"])
def add_bulk():
    path = request.form.get("path", "").strip()
    if not os.path.exists(path):
        return render_template_string(ADD_TMPL, active_page="add",
            error=f"File not found: {path}", success=None)
    with open(path, encoding="utf-8") as f:
        new_docs = json.load(f)
    ir.update_corpus(new_docs)
    return render_template_string(ADD_TMPL, active_page="add",
        success=f"Added {len(new_docs)} documents. Corpus now has {len(ir.doc_ids):,} documents.",
        error=None)


@app.route("/stats")
def stats():
    total  = len(ir.doc_ids)
    vocab  = len(ir.bm25.idf) if hasattr(ir.bm25, "idf") else "N/A"
    avg    = round(sum(len(t) for t in ir.corpus_tokens) / total, 1) if total else 0
    return render_template_string(STATS_TMPL,
        active_page="stats",
        total_docs=f"{total:,}",
        vocab_size=f"{vocab:,}" if isinstance(vocab, int) else vocab,
        avg_tokens=avg)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Starting Financial IR System at http://localhost:5000")
    app.run(debug=True, port=5000)