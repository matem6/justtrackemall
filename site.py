#!/usr/bin/env python3
import sqlite3
import os

# Percorso del database e file di output
DB_FILE = "../offerid_tcg.sqlite3"  # oppure, se preferisci, il database TCG
OUTPUT_DIR = "docs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")

# Mapping per emoji bandiere e per il dominio di Amazon:
FLAG_MAPPING = {
    "it": ("🇮🇹", "it"),
    "uk": ("🇬🇧", "co.uk"),
    "de": ("🇩🇪", "de"),
    "fr": ("🇫🇷", "fr"),
    "es": ("🇪🇸", "es"),
    "us": ("🇺🇸", "com"),
    "ca": ("🇨🇦", "ca"),
    # Aggiungi altri mapping se necessario
}

REF_TAG = {
    "it": "justtrack-it-21",
    "de": "justtrack-de-21",
    "fr": "justtrack-fr-21",
    "es": "justtrack-es-21",
}

def generate_html():
    # Connetti al database e recupera i dati (senza l'offerid e il cooldown)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT asin, title, country, price FROM offerid")
    rows = cursor.fetchall()
    conn.close()

    # Raggruppa per ASIN
    grouped = {}
    for row in rows:
        asin = row["asin"]
        if asin not in grouped:
            grouped[asin] = []
        grouped[asin].append(row)

    # Costruisci il contenuto HTML utilizzando il tema Darkly di Bootswatch e i colori brand
    html = """<!doctype html>
<html lang="it">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <title>Prodotti Tracciati</title>
    <!-- Bootstrap Darkly Theme (Bootswatch) -->
    <link href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.0/dist/darkly/bootstrap.min.css" rel="stylesheet">
    <style>
      :root {
        --brand-orange: #ff8201;
        --brand-teal:   #16aeb1;
      }
      body {
        padding-top: 20px;
        background-color: #2b2b2b;
        color: #eaeaea;
      }
      header {
        text-align: center;
        margin-bottom: 20px;
      }
      header img {
        max-width: 100%;
        height: auto;
        max-height: 50px; /* Altezza massima ridotta da 76px a 50px */
      }
      h1 {
        color: var(--brand-orange);
      }
      .card {
        background-color: #3a3f44;
        border: none;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
        border-top: 4px solid var(--brand-orange);
      }
      .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #d5d2d2;
      }
      .list-group-item {
        background-color: #3a3f44;
        border: none;
        padding: .75rem 1.25rem;
      }
      .list-group-item a {
        text-decoration: none;
        color: var(--brand-teal);
      }
      .list-group-item a:hover {
        text-decoration: underline;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <header>
        <!-- Assicurati che "logo.png" sia presente nella cartella "docs" o modifica il percorso -->
        <img src="logo.png" alt="Logo">
      </header>
      <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 g-4">
"""

    # Ordina gli ASIN e crea una card per ciascuno
    for asin in sorted(grouped.keys()):
        variants = grouped[asin]
        variants.sort(key=lambda x: x["country"].lower())
        title = variants[0]["title"]

        html += f"""        <div class="col">
          <div class="card h-100">
            <div class="card-body">
              <h5 class="card-title">[{asin}] {title}</h5>
              <!-- Inserisco una intestazione per il prezzo -->
              <p class="mb-2"><strong>Limite di segnalazione:</strong></p>
              <ul class="list-group list-group-flush">
"""
        # Per ogni variante, mostra solo l'icona della nazione e il prezzo (senza ripetere "Prezzo:" in ogni riga)
        for variant in variants:
            country_raw = variant["country"].lower()
            flag, domain = FLAG_MAPPING.get(country_raw, (variant["country"], variant["country"]))
            price = variant["price"]
            formatted_price = f"{price/100:.2f}".replace('.', ',')
            amazon_url = f"https://www.amazon.{domain}/dp/{asin}?tag={REF_TAG.get(country_raw, 'justtrack-21')}"
            html += f'                <li class="list-group-item"><a href="{amazon_url}" target="_blank">{flag} {formatted_price}€</a></li>\n'
        html += """              </ul>
            </div>
          </div>
        </div>
"""
    html += """      </div>
    </div>
    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("Sito statico generato con successo in", OUTPUT_FILE)

if __name__ == '__main__':
    generate_html()
