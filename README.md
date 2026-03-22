# Anisearch.de Anime Synchronisations-Tracker

> ⚠️ **HINWEIS: Projekt in Entwicklung**
> 
> Dieser Code befindet sich noch in aktiver Entwicklung. Features, Dokumentation und die API können sich ändern. Aktuelle Bugs und Unvollständigkeiten sollten erwartet werden. Wenn ihr Bugs entdeckt oder Verbesserungsvorschläge habt, bitte über Issues berichten!

Ein vollständig integriertes Python-Backend und HTML-Frontend-Projekt zur Verfolgung von deutschen Anime-Synchronisationen auf [anisearch.de](https://www.anisearch.de).

## 📋 Inhaltsverzeichnis

- [Status](#-status)
- [Funktionen](#-funktionen)
- [Anforderungen](#-anforderungen)
- [Installation](#-installation)
- [Verwendung](#-verwendung)
- [Projektstruktur](#-projektstruktur)
- [API-Dokumentation](#-api-dokumentation)
- [Technologie-Stack](#-technologie-stack)
- [Lizenz](#lizenz)

## 🚧 Status

**Aktueller Entwicklungsstand:** Early Development (WIP - Work in Progress)

### Was ist fertig ✅
- Basis-Backend mit Flask
- HTML-Frontend-Interface
- Anime-Daten Scraping (kommend/aktuell)
- JSON/JavaScript Datenexport
- Grundlegende Filterung und Suche

### Was ist noch in Arbeit 🔄
- Fehlerbehandlung optimieren
- Performance-Verbesserungen
- Unit Tests
- Deployment-Dokumentation
- Docker-Unterstützung
- Caching-Strategien
- Frontend-Optimierungen

### Bekannte Probleme 🐛
- Scraping kann bei Änderungen auf anisearch.de brechen
- Rate-Limiting ist nicht implementiert
- Keine Real-Time-Updates
- Mobile-View könnte verbessert werden

## ✨ Funktionen

### Backend (`scrape_anisearch_fixed.py`)
- ✅ **Automatische Scraping** von anisearch.de für kommende und aktuelle deutsche Synchronisationen
- ✅ **Automatische Abhängigkeits-Installation** - Required Python-Pakete werden automatisch installiert
- ✅ **JSON/JavaScript Datenexport** - Speichert Daten in JSON und JS-Dateien zur Weiterverarbeitung
- ✅ **Flask-API** - RESTful API-Endpoint für Datenzugriff (`/api/anime-data`)
- ✅ **Fallback-Mechanismus** - Demo-Daten bei Scraping-Fehlern
- ✅ **Caching** - In-Memory-Daten für schnelle API-Responses

### Frontend (`index.html`)   (Anime Synchro Tracker v11.0.1)
- 🎨 **Responsive Web-Interface** mit modernes HTML5/CSS3 Design
- 📱 **Mobile-friendly** Datentabellen und Filter
- 🔍 **Live-Suche** und Filterung von Anime-Einträgen
- 📊 **Daten-Visualisierung** für kommende und aktuelle Dubs
- ⚡ **JavaScript-Datenintegration** zum Laden von Anime-Daten
- 🎬 **Deutsche Synchronisations-Details** mit Statusanzeige

## 🔧 Anforderungen

### Systemanforderungen
- **Python:** 3.7+
- **Browser:** Moderner Browser mit HTML5/CSS3-Unterstützung
- **OS:** Windows, macOS, Linux

### Python-Abhängigkeiten

Die folgenden Pakete werden **automatisch installiert**:

```
requests>=2.28.0         # HTTP-Anfragen
beautifulsoup4>=4.11.0   # HTML-Parsing
flask>=2.0.0             # Web-Framework
```

## 📥 Installation

### 1. Repository klonen
```bash
git clone https://github.com/StrikerLUL/anime-ger-dub-tracker-WORK-IN-PROGRESS.git
cd anime-ger-dub-tracker-WORK-IN-PROGRESS
```

### 2. Python-Environment erstellen (optional aber empfohlen)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Projekt starten
```bash
python scrape_anisearch_fixed.py
```

Das war's! Die Abhängigkeiten werden automatisch installiert.

## 🚀 Verwendung

### Backend starten
```bash
python scrape_anisearch_fixed.py
```

**Ausgabe:**
```
======================================================================
🎬 ANISEARCH.DE SCRAPER v2.1 - Deutsche Synchronisationen
======================================================================

✅ requests bereits installiert
✅ beautifulsoup4 bereits installiert
✅ flask bereits installiert

📥 Lade Anime-Daten...
🎬 Scrape KOMMENDE Deutsche Synchronisationen...
✅ 45 kommende Dubs gefunden
🔴 Scrape AKTUELLE Deutsche Synchronisationen...
✅ 180 aktuelle Dubs gefunden

✅ Daten aktualisiert: 45 kommend, 180 aktuell
✅ JSON gespeichert: anime_data.json
✅ JavaScript-Datei gespeichert: anime_data.js

======================================================================
🚀 Starte Server...
📱 Öffne im Browser: http://localhost:5000
🛑 Zum Beenden: CTRL+C drücken
======================================================================
```

### Zugriff auf die Anwendung
Öffne deinen Browser und navigiere zu:
```
http://localhost:5000
```

### Server beenden
Drücke `CTRL+C` im Terminal.

## 📁 Projektstruktur

```
anisearch-tracker/
├── scrape_anisearch_fixed.py   # Python Backend & Flask Server
├── index.html                  # HTML Frontend Interface
├── anime_data.json            # Generierte Anime-Daten (JSON)
├── anime_data.js              # Generierte Anime-Daten (JavaScript)
└── README.md                  # Diese Datei
```

## 🔌 API-Dokumentation

### GET `/`
Serviert die HTML-Trackerseite.

**Response:**
```html
HTML-Seite mit Anime-Tabellen und Filterung
```

---

### GET `/api/anime-data`
Liefert alle gecachten Anime-Daten im JSON-Format.

**Response (200):**
```json
{
  "kommende": [
    {
      "title": "Anime-Name",
      "studio": "Studio-Name",
      "startDate": "2026-01-XX",
      "dubbed": true
    }
  ],
  "aktuelle": [
    {
      "title": "Anime-Name",
      "studio": "Studio-Name",
      "startDate": "2025-XX-XX",
      "episodes": 12,
      "dubbed": true
    }
  ],
  "timestamp": "2026-01-11T10:00:00.123456"
}
```

**Error Response (404):**
```json
{
  "error": "Keine Daten verfügbar"
}
```

---

### GET `/anime_data.json`
Serveert die lokal gespeicherte JSON-Datei.

**Response (200):**
```json
{
  "kommende": [...],
  "aktuelle": [...],
  "timestamp": "...",
  "source": "anisearch.de",
  "version": "2.1"
}
```

---

## 💻 Technologie-Stack

| Komponente | Technologie |
|-----------|--------------|
| **Backend** | Python 3.7+ |
| **Web-Framework** | Flask 2.0+ |
| **HTML-Parsing** | BeautifulSoup4 |
| **HTTP-Client** | Requests |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Datenspeicherung** | JSON, JavaScript |
| **Server** | Flask Dev Server (lokale Entwicklung) |

## 🔄 Workflow

```
1. Python-Skript startet
   ↓
2. Abhängigkeiten installieren (falls fehlen)
   ↓
3. anisearch.de scrapen (kommende + aktuelle Dubs)
   ↓
4. Daten in JSON/JS speichern
   ↓
5. Flask-Server auf Port 5000 starten
   ↓
6. HTML-Interface mit Daten laden
   ↓
7. Browser: http://localhost:5000 öffnen
```

## ⚠️ Hinweise

- **Scraping-Berechtigungen:** Bitte überprüfen Sie die Nutzungsbedingungen von anisearch.de vor der Verwendung
- **Rate-Limiting:** Das Skript enthält kein Rate-Limiting - verwenden Sie es verantwortungsvoll
- **Fehlerbehandlung:** Bei Scraping-Fehlern wird automatisch auf Demo-Daten ausgewichen
- **Daten-Aktualität:** Die Daten werden beim Skriptstart aktualisiert, nicht in Echtzeit
- **Instabilität:** Da das Projekt noch in Entwicklung ist, sollten Bugs und Breaking Changes erwartet werden

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"
**Lösung:** Das Skript installiert Abhängigkeiten automatisch. Falls das fehlschlägt:
```bash
pip install requests beautifulsoup4 flask
```

### Problem: Port 5000 ist bereits in Verwendung
**Lösung:** Beende andere Anwendungen auf Port 5000 oder bearbeite die Port-Nummer in `scrape_anisearch_fixed.py`:
```python
app.run(debug=False, host='localhost', port=5001)  # Anderer Port
```

### Problem: "HTML-Datei nicht gefunden"
**Lösung:** Stelle sicher, dass `index.html` im gleichen Verzeichnis wie `scrape_anisearch_fixed.py` liegt.

### Problem: Scraping funktioniert nicht
**Lösung:** anisearch.de könnte das HTML-Layout geändert haben. Bitte öffne ein GitHub Issue mit Details zur fehlgeschlagenen Scraping-Operation.

## 📊 Beispiel-Daten

Das Projekt generiert automatisch Daten wie:

**Kommende Synchronisationen:**
```json
{
  "title": "Beispiel Anime",
  "studio": "Anime Studio",
  "startDate": "2026-02-15",
  "synopsis": "Kurze Beschreibung...",
  "genres": ["Action", "Drama"],
  "dubbed": true
}
```

**Aktuelle Synchronisationen:**
```json
{
  "title": "Laufender Anime",
  "studio": "Anime Studio",
  "startDate": "2025-10-01",
  "episodes": 12,
  "status": "Airing",
  "dubbed": true,
  "dubStatus": "In Produktion"
}
```

## 🔐 Sicherheit & Datenschutz

- Das Projekt speichert **keine persönlichen Daten**
- Alle Daten stammen von anisearch.de (öffentliche Quelle)
- Der Server läuft nur **lokal** (localhost:5000)
- Keine externen APIs werden kontaktiert (außer anisearch.de zum Scraping)

## 🤝 Beitragen

Beiträge sind willkommen! Bitte:

1. **Fork** das Repository
2. Erstelle einen **Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit** deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. **Push** zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen **Pull Request**

### Für Entwickler
Wenn ihr das Projekt forken möchtet um zu helfen:
- Achtet auf die bekannten Probleme (siehe Status-Sektion)
- Bitte testet gründlich, bevor ihr PRs öffnet
- Schreibt gerne Issues für neue Features oder Bugs die ihr findet

**Made with ❤️ for Anime Fans**

*Dieses Projekt wird von der Community gepflegt und ist nicht offiziell mit anisearch.de verbunden.*
