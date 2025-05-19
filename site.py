#!/usr/bin/env python3
"""
Genera index.html leggendo dalla tabella MySQL `offerid_jte`.
"""

import os
import mysql.connector   # pip install mysql-connector-python

# ──────────────── CONFIGURAZIONE DB (adatta a tuo ambiente) ────────────────
DB_CFG = {
    "host":       "10.0.0.67",
    "port":       3306,
    "user":       "java",     # ← cambia
    "password":   "123456",     # ← cambia
    "database":   "notification",    # ← cambia
    "use_unicode": True,
}
TABLE_NAME   = "offerid_jte"     # ← fisso: SOLO jte
OUTPUT_DIR   = "/root/bot/web/docs"
OUTPUT_FILE  = os.path.join(OUTPUT_DIR, "index.html")
# ────────────────────────────────────────────────────────────────────────────

FLAG_MAPPING = {
    "it": ("🇮🇹", "it"),   "uk": ("🇬🇧", "co.uk"),
    "de": ("🇩🇪", "de"),   "fr": ("🇫🇷", "fr"),
    "es": ("🇪🇸", "es"),   "us": ("🇺🇸", "com"),
    "ca": ("🇨🇦", "ca"),
}
REF_TAG = {
    "it": "justtrack-it-21",
    "de": "justtrack-de-21",
    "fr": "justtrack-fr-21",
    "es": "justtrack-es-21",
}

def generate_html() -> None:
    # ─── leggi dati ─────────────────────────────────────────────────────────
    query = f"SELECT asin, title, country, price FROM `{TABLE_NAME}`"
    conn = mysql.connector.connect(**DB_CFG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close(); conn.close()

    # ─── raggruppa per ASIN ────────────────────────────────────────────────
    grouped = {}
    for r in rows:
        grouped.setdefault(r["asin"], []).append(r)

    # ─── componi HTML ──────────────────────────────────────────────────────
    html = [HTML_HEADER]
    for asin in sorted(grouped):
        variants = sorted(grouped[asin], key=lambda v: v["country"].lower())
        title = next((v["title"] for v in variants
                      if v["country"].lower() == "it"), variants[0]["title"])

        html.append(f"""        <div class="col">
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title">[{asin}] {title}</h5>
              <p class="mb-2"><strong>Limite di segnalazione:</strong></p>
              <ul class="list-group list-group-flush">
""")
        for v in variants:
            ctry = v["country"].lower()
            flag, domain = FLAG_MAPPING.get(ctry, (ctry.upper(), ctry))
            price = f"{v['price']/100:.2f}".replace('.', ',')
            url = f"https://www.amazon.{domain}/dp/{asin}?tag={REF_TAG.get(ctry,'justtrack-21')}"
            html.append(
                f'                <li class="list-group-item"><a href="{url}"'
                f' target="_blank">{flag} {price}€</a></li>\n'
            )
        html.append("""              </ul>
            </div>
          </div>
        </div>
""")
    html.append(HTML_FOOTER)

    # ─── scrivi file ───────────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write("".join(html))
    print("Sito statico generato in", OUTPUT_FILE)

# ——— frammenti fissi di pagina —————————————————————————————
HTML_HEADER = """<!doctype html>
<html lang="it">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <title>Prodotti Tracciati</title>
    <link href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.0/dist/darkly/bootstrap.min.css" rel="stylesheet">
    <style>
      :root { --brand-orange:#ff8201; --brand-teal:#16aeb1; }
      body   { padding-top:20px; background:#2b2b2b; color:#eaeaea; }
      header { text-align:center; margin-bottom:20px; }
      header img { max-width:100%; height:auto; max-height:50px; }
      h1     { color:var(--brand-orange); }
      .card  { background:#3a3f44; border:none; box-shadow:0 2px 5px rgba(0,0,0,.5);
               border-top:4px solid var(--brand-orange); }
      .card-title     { font-size:1.1rem; font-weight:600; color:#d5d2d2; }
      .list-group-item{ background:#3a3f44; border:none; padding:.75rem 1.25rem; }
      .list-group-item a{ text-decoration:none; color:var(--brand-teal); }
      .list-group-item a:hover{ text-decoration:underline; }
    </style>
  </head>
  <body>
    <div class="container">
      <header><img src="logo.png" alt="Logo"></header>
      <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 g-4">
"""

HTML_FOOTER = """      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""

# ——— esecuzione diretta ————————————————————————————————————
if __name__ == "__main__":
    generate_html()
