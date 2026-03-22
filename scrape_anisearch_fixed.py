#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
anisearch.de Scraper für Deutsche Anime Synchronisationen
Version 4.0 - Playwright-basiert (headless Browser)

Benötigt: pip install playwright flask
          python -m playwright install chromium

Starte einfach mit: python scrape_anisearch_fixed.py
Oder per Doppelklick auf: SERVER STARTEN.bat
"""

import json
import sys
import os
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request

# ─── Flask-App Setup ──────────────────────────────────────────────────────────
app = Flask(__name__)

# Globaler Cache
CACHED_DATA: dict = {
    'kommende':      [],
    'aktuelle':      [],
    'abgeschlossen': [],
    'timestamp':     None,
}
SCRAPING_FLAG = {'active': False}  # Getrennt, damit Typen klar bleiben
DATA_LOCK = threading.Lock()

# ─── Scraper-Konstanten ───────────────────────────────────────────────────────
BASE_URL  = "https://www.anisearch.de"
HEADERS   = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MAX_PAGES = 5      # Max Seiten pro Kategorie
DELAY_MS  = 1500   # Wartezeit zwischen Seitenladevorgängen (ms)


def ensure_dependencies():
    """Installiere fehlende Pakete automatisch."""
    missing = []
    try:
        import flask
    except ImportError:
        missing.append('flask')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        missing.append('playwright')

    if missing:
        print(f"📦 Installiere fehlende Pakete: {', '.join(missing)}")
        os.system(f'"{sys.executable}" -m pip install {" ".join(missing)} -q')

    # Playwright Chromium
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
    except Exception:
        print("📦 Installiere Playwright Chromium...")
        os.system(f'"{sys.executable}" -m playwright install chromium')


def accept_cookies(page):
    """Akzeptiere den Cookie-Banner falls er erscheint."""
    try:
        consent = page.locator('text=ALLES AKZEPTIEREN')
        if consent.count() > 0:
            consent.first.click()
            page.wait_for_timeout(1500)
            print("✅ Cookie-Banner akzeptiert")
    except Exception:
        pass


def parse_anime_list(page):
    """Extrahiere Anime-Daten von der aktuell geladenen Seite."""
    results = []
    try:
        page.wait_for_selector('.covers', timeout=8000)
    except Exception:
        return results

    items = page.locator('ul.covers li a.anime-item').all()
    for item in items:
        try:
            href     = item.get_attribute('href') or ''
            title_el = item.locator('span.title')
            title    = title_el.inner_text().strip() if title_el.count() > 0 else ''
            date_el  = item.locator('span.date')
            date_str = date_el.inner_text().strip() if date_el.count() > 0 else ''
            img_el   = item.locator('img')
            img      = img_el.get_attribute('src') or '' if img_el.count() > 0 else ''

            # ID aus href extrahieren
            anime_id = 0
            if '/' in href:
                part = href.split('/')[-1]
                if ',' in part:
                    try:
                        anime_id = int(part.split(',')[0])
                    except Exception:
                        pass

            if title:
                results.append({
                    'id':    anime_id,
                    'title': title,
                    'url':   f"{BASE_URL}/{href}",
                    'image': img,
                    'info':  date_str,
                    'year':  extract_year(date_str),
                    'type':  extract_type(date_str),
                })
        except Exception:
            continue
    return results


def extract_year(date_str: str) -> int:
    """Extrahiere das Jahr aus dem Datum-String."""
    import re
    m = re.search(r'\((\d{4})\)', date_str)
    if m:
        return int(m.group(1))
    m = re.search(r'\b(20\d{2})\b', date_str)
    if m:
        return int(m.group(1))
    return 0


def extract_type(date_str: str) -> str:
    """Extrahiere den Anime-Typ."""
    types = ['TV-Serie', 'Film', 'OVA', 'Web', 'TV-Spezial', 'Bonus', 'Musikvideo']
    for t in types:
        if t in date_str:
            return t
    return 'Anime'


def scrape_category(url_params: str, label: str, max_pages: int = MAX_PAGES, max_retries: int = 2) -> list:
    """Scrape alle Seiten einer Kategorie mit Playwright. Mit Retry-Logik."""
    from playwright.sync_api import sync_playwright

    for attempt_idx in range(max_retries):
        attempt = attempt_idx + 1
        try:
            all_results: list = []
            print(f"\n{'='*60}")
            print(f"🔍 Scrape: {label} (Versuch {attempt}/{max_retries})")
            print(f"{'='*60}")

            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=HEADERS['User-Agent'],
                    locale='de-DE'
                )
                page = context.new_page()

                # Erste Seite laden
                url = f"{BASE_URL}/anime/index/page-1?{url_params}"
                print(f"📄 Lade Seite 1: {url}")
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(DELAY_MS)
                accept_cookies(page)
                page.wait_for_timeout(DELAY_MS)

                # Gesamt-Seitenanzahl ermitteln
                total_pages = 1
                try:
                    import re
                    nav_info = page.locator('.pagenav-info').inner_text(timeout=3000)
                    m = re.search(r'von (\d+)', nav_info)
                    if m:
                        total_pages = min(int(m.group(1)), max_pages)
                except Exception:
                    pass
                print(f"   → {total_pages} Seite(n) gefunden")

                # Seite 1 parsen
                page1_results = parse_anime_list(page)
                all_results.extend(page1_results)
                print(f"   ✅ Seite 1: {len(page1_results)} Anime")

                # Restliche Seiten
                for p_num in range(2, total_pages + 1):
                    url = f"{BASE_URL}/anime/index/page-{p_num}?{url_params}"
                    print(f"📄 Lade Seite {p_num}: {url}")
                    try:
                        page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        page.wait_for_timeout(DELAY_MS)
                        results = parse_anime_list(page)
                        all_results.extend(results)
                        print(f"   ✅ Seite {p_num}: {len(results)} Anime")
                    except Exception as e:
                        print(f"   ⚠️  Fehler auf Seite {p_num}: {e}")
                        break

                browser.close()

            # Duplikate entfernen (anhand ID)
            seen = set()
            unique = []
            for a in all_results:
                if a['id'] not in seen:
                    seen.add(a['id'])
                    unique.append(a)

            print(f"\n✅ {label}: {len(unique)} Anime gesamt\n")
            return unique

        except Exception as e:
            print(f"⚠️  Versuch {attempt} fehlgeschlagen: {e}")
            if attempt_idx < max_retries - 1:
                print(f"⏳ Warte 5 Sekunden vor erneutem Versuch...")
                time.sleep(5)

    print(f"❌ {label}: Alle Versuche fehlgeschlagen")
    return []


def run_scraper():
    """Haupt-Scraper: Lädt kommende, aktuelle und abgeschlossene Dubs."""
    with DATA_LOCK:
        if SCRAPING_FLAG['active']:
            print("⚠️  Scraper läuft bereits, überspring...")
            return
        SCRAPING_FLAG['active'] = True

    try:
        print("\n" + "="*60)
        print("🎬 ANISEARCH SCRAPER v4.0 - Deutsche Synchronisationen")
        print("="*60)

        # dubbed_status=3 → Geplant / Bald verfügbar
        kommende = scrape_category(
            url_params='char=all&dubbed=de&dubbed_status=3&sort=date&order=asc',
            label='Bald verfügbar (Geplante Deutsche Synchronisationen)'
        )

        # dubbed_status=2 → Laufend / Kürzlich erschienen
        aktuelle = scrape_category(
            url_params='char=all&dubbed=de&dubbed_status=2&sort=date&order=desc',
            label='Kürzlich erschienen (Laufende Deutsche Synchronisationen)'
        )

        # dubbed_status=1 → Abgeschlossen
        abgeschlossen = scrape_category(
            url_params='char=all&dubbed=de&dubbed_status=1&sort=date&order=desc',
            label='Abgeschlossene Deutsche Synchronisationen',
            max_pages=3  # Weniger Seiten, da sehr viele
        )

        # Daten cachen
        with DATA_LOCK:
            CACHED_DATA['kommende']      = kommende
            CACHED_DATA['aktuelle']      = aktuelle
            CACHED_DATA['abgeschlossen'] = abgeschlossen
            CACHED_DATA['timestamp']     = datetime.now().isoformat()
            SCRAPING_FLAG['active']      = False

        # JSON speichern für Offline-Nutzung
        save_json(kommende, aktuelle, abgeschlossen)

        total = len(kommende) + len(aktuelle) + len(abgeschlossen)
        print(f"\n🚀 Fertig! {len(kommende)} kommende + {len(aktuelle)} aktuelle + {len(abgeschlossen)} abgeschlossene Dubs.")
        print(f"📊 Gesamt: {total} deutsche Synchronisationen")
        return kommende, aktuelle, abgeschlossen

    except Exception as e:
        print(f"❌ Scraper-Fehler: {e}")
        SCRAPING_FLAG['active'] = False
        return [], [], []


def save_json(kommende, aktuelle, abgeschlossen, path='anime_data.json'):
    """Speichere als JSON-Datei für Offline-Nutzung."""
    data = {
        'kommende':      kommende,
        'aktuelle':      aktuelle,
        'abgeschlossen': abgeschlossen,
        'timestamp':     datetime.now().isoformat(),
        'source':        'anisearch.de',
        'version':       '4.0'
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    total = len(kommende) + len(aktuelle) + len(abgeschlossen)
    print(f"💾 JSON gespeichert: {path} ({total} Animes)")


def auto_refresh_loop(interval_hours=6):
    """Automatisch alle N Stunden neu scrapen."""
    while True:
        time.sleep(interval_hours * 3600)
        print(f"\n🔄 Auto-Refresh gestartet (alle {interval_hours}h)...")
        try:
            run_scraper()
        except Exception as e:
            print(f"⚠️  Auto-Refresh Fehler: {e}")


# ─── Flask-Endpunkte ──────────────────────────────────────────────────────────

HTML_FILE = "Anime Synchro Tracker v11.0.1.html"


@app.route('/')
def serve_index():
    """Serviere den HTML-Tracker."""
    if os.path.exists(HTML_FILE):
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return "HTML-Datei nicht gefunden!", 404


@app.route('/api/anime-data')
def api_anime_data():
    """Haupt-API: liefert die gecachten Daten."""
    with DATA_LOCK:
        if CACHED_DATA['timestamp']:
            return jsonify({
                'kommende':      CACHED_DATA['kommende'],
                'aktuelle':      CACHED_DATA['aktuelle'],
                'abgeschlossen': CACHED_DATA['abgeschlossen'],
                'timestamp':     CACHED_DATA['timestamp'],
                'scraping':      SCRAPING_FLAG['active'],
                'total':         len(CACHED_DATA['kommende']) + len(CACHED_DATA['aktuelle']) + len(CACHED_DATA['abgeschlossen']),
                'source':        'live'
            })

    # Fallback: Lade JSON-Datei falls vorhanden
    if os.path.exists('anime_data.json'):
        with open('anime_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            data['source'] = 'cache'
            return jsonify(data)

    return jsonify({
        'error':    'Noch keine Daten – Scraping läuft...',
        'scraping': SCRAPING_FLAG['active']
    }), 503


@app.route('/api/refresh')
def api_refresh():
    """Manueller Scraper-Start via API."""
    if SCRAPING_FLAG['active']:
        return jsonify({'status': 'Scraping läuft bereits...', 'scraping': True})
    t = threading.Thread(target=run_scraper, daemon=True)
    t.start()
    return jsonify({'status': 'Scraping gestartet...', 'scraping': True})


@app.route('/api/status')
def api_status():
    """Server-Status."""
    with DATA_LOCK:
        kom = len(CACHED_DATA['kommende'])
        akt = len(CACHED_DATA['aktuelle'])
        abg = len(CACHED_DATA['abgeschlossen'])
    return jsonify({
        'status':        'online',
        'kommende':      kom,
        'aktuelle':      akt,
        'abgeschlossen': abg,
        'timestamp':     CACHED_DATA['timestamp'],
        'scraping':      SCRAPING_FLAG['active'],
        'version':       '4.0'
    })


@app.route('/anime_data.json')
def serve_json():
    if os.path.exists('anime_data.json'):
        return send_from_directory('.', 'anime_data.json')
    return jsonify({'error': 'Keine Datei'}), 404


# CORS für direkten HTML-Datei-Aufruf und alle Quellen
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# ─── Hauptprogramm ───────────────────────────────────────────────────────────

def main():
    print("="*60)
    print("🎬 ANIME SYNCHRO TRACKER - SERVER v4.0")
    print("="*60)
    print()
    print("abhängigkeiten werden geprüft...")
    ensure_dependencies()
    print()
    print("1. [Scraper + Server] Scrapt Anisearch & startet Server")
    print("2. [Nur Server]       Startet Server mit gecachten Daten")
    print("3. [Nur Scraper]      Scrapt Anisearch, kein Server")
    print()

    choice = input("Auswahl (1/2/3) [Standard: 1]: ").strip() or '1'

    if choice == '3':
        run_scraper()
        return

    if choice in ('1', ''):
        print("\n📥 Starte ersten Scraping-Vorgang im Hintergrund...")

        # Optional: gecachte Daten sofort laden damit Server sofort Daten hat
        if os.path.exists('anime_data.json'):
            print("💾 Lade gecachte Daten aus anime_data.json...")
            try:
                with open('anime_data.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                with DATA_LOCK:
                    CACHED_DATA['kommende']      = saved.get('kommende', [])
                    CACHED_DATA['aktuelle']      = saved.get('aktuelle', [])
                    CACHED_DATA['abgeschlossen'] = saved.get('abgeschlossen', [])
                    CACHED_DATA['timestamp']     = saved.get('timestamp', None)
                total = len(CACHED_DATA['kommende']) + len(CACHED_DATA['aktuelle']) + len(CACHED_DATA['abgeschlossen'])
                print(f"   → {total} Animes aus Cache geladen (werden im Hintergrund aktualisiert)")
            except Exception as e:
                print(f"   ⚠️  Cache-Fehler: {e}")

        # Scraper im Hintergrund starten
        t = threading.Thread(target=run_scraper, daemon=True)
        t.start()

        # Auto-Refresh alle 6 Stunden
        t2 = threading.Thread(target=auto_refresh_loop, args=(6,), daemon=True)
        t2.start()

    print("\n" + "="*60)
    print("🚀 Server läuft auf http://localhost:5000")
    print("📡 API:           http://localhost:5000/api/anime-data")
    print("🔄 Refresh:       http://localhost:5000/api/refresh")
    print("📊 Status:        http://localhost:5000/api/status")
    print("🛑 Beenden: CTRL+C drücken")
    print("="*60 + "\n")

    try:
        app.run(debug=False, host='localhost', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n✅ Server beendet.")


if __name__ == '__main__':
    main()
