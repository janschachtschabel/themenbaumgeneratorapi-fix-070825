# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.4] - 2025-01-07

### Hinzugefügt
- **Intelligente Bildungsstufen-Extraktion**: Automatische Extraktion lesbarer Bildungsstufen-Informationen aus URIs
  - **URI-Parsing**: Extrahiert den letzten Segment aus Bildungsstufen-URIs (z.B. "sekundarstufe_2" aus "http://w3id.org/openeduhub/vocabs/educationalContext/sekundarstufe_2")
  - **Lesbarkeitsverbesserung**: Wandelt Unterstriche in Leerzeichen um ("sekundarstufe_2" → "sekundarstufe 2")
  - **Prompt-Integration**: Fügt lesbare Bildungsstufen-Information als "Zielgruppe/Bildungsstufe" zu den Kontext-Informationen hinzu
  - **Mehrfach-URI-Unterstützung**: Verarbeitet mehrere Bildungsstufen-URIs korrekt

### Verbessert
- **Kontextuelle Themengenerierung**: AI erhält jetzt sowohl technische URIs als auch verständliche Bildungsstufen-Informationen
  - **Bessere Zielgruppenanpassung**: Themenbaumgenerierung berücksichtigt spezifische Bildungsstufen
  - **Altersgerechte Inhalte**: Automatische Anpassung von Komplexität und Themenwahl
  - **Erweiterte Kontext-Informationen**: Vollständige Prompt-Kontextualisierung für alle Generierungsschritte

### Technische Details

**Neue Funktionen:**
- `extract_educational_context_info()`: Zentrale Funktion zur URI-Extraktion und Lesbarkeitsverbesserung
  - Robuste URI-Parsing-Logik
  - Behandlung verschiedener URI-Formate
  - Automatische Textnormalisierung

**Geänderte Dateien:**

**`main.py`:**
- Neue `extract_educational_context_info()` Funktion (Zeilen 42-72)
  - URI-Parsing und Lesbarkeitsverbesserung
  - Robuste Behandlung verschiedener URI-Formate
- Erweiterte Kontext-Generierung (Zeilen 219-230):
  ```python
  # Extrahiere lesbare Bildungsstufen-Information
  readable_context = extract_educational_context_info(topic_tree_request.educational_context_uri)
  if readable_context:
      context_info.append(f"Zielgruppe/Bildungsstufe: {readable_context}")
  ```
- Integration in alle Themenbaumgenerierungen für bildungsstufengerechte Inhalte

**Beispiel:**
```
Input-URI: http://w3id.org/openeduhub/vocabs/educationalContext/sekundarstufe_2
Prompt-Kontext: 
  Bildungsstufe-URIs: http://w3id.org/openeduhub/vocabs/educationalContext/sekundarstufe_2
  Zielgruppe/Bildungsstufe: sekundarstufe 2
```

## [1.2.3] - 2025-01-07

### Hinzugefügt
- **Neuer API-Endpunkt `/generate-collection-description`**: Eigenständiger Endpunkt zur Generierung von Sammlungsbeschreibungen
  - **Parameter**: `text_context` (Text und Kontext), `max_description_length` (Standard: 400), `model` (Standard: gpt-4.1-mini)
  - **Output**: Sauberer Fließtext ohne JSON-Strukturen oder Formatierungszeichen
  - **Intelligente Post-Processing**: Automatische Extraktion von Beschreibungstext falls JSON zurückgegeben wird
  - **Vollständige Swagger-Dokumentation**: Detaillierte API-Beschreibung mit Beispielen

### Verbessert
- **Prompt-Optimierung für Textlänge**: DESCRIPTION_PROMPT_TEMPLATE und System-Message verstärkt
  - Explizite Anweisung zur Nutzung der vollständigen erlaubten Zeichenlänge
  - Ermutigung zu ausführlichen, detaillierten Beschreibungen mit Beispielen
  - Verbesserung der Ausgabequalität durch gezielte Längenanforderungen

### Behoben
- **JSON-Output verhindert**: Prompt und Post-Processing verhindern ungewollte JSON-Strukturen
- **Escape-Zeichen entfernt**: Vollständige Bereinigung von `\n`, `\r`, `\t` und mehrfachen Leerzeichen
  - **Neuer Endpunkt**: Intelligente Post-Processing für `/generate-collection-description`
  - **Haupt-Endpunkt**: Text-Bereinigung für alle Beschreibungen in `/generate-topic-tree` via `clean_description_text()`
  - **Konsistente Ausgabe**: Beide Endpunkte liefern jetzt saubere Fließtexte ohne störende Formatierungszeichen
- **OpenAI-Client Integration**: Korrekte Client-Initialisierung analog zum bestehenden Endpunkt

### Technische Details

**Neue Dateien:**
- `src/DTOs/description_request.py`: Request-Modell für den neuen Endpunkt

**Geänderte Dateien:**

**`src/prompts.py`:**
- Neuer DESCRIPTION_PROMPT_TEMPLATE (Zeilen 148-170)
- Verstärkte Längenanforderungen und explizite Plain-Text-Anweisungen

**`main.py`:**
- Neuer `/generate-collection-description` Endpunkt (Zeilen 326-393)
- Import von DescriptionRequest und DESCRIPTION_PROMPT_TEMPLATE (Zeilen 14-15)
- Intelligente Post-Processing mit JSON-Extraktion (Zeilen 398-418)
- Text-Bereinigung für alle Formatierungszeichen (Zeilen 420-428)

**`src/structured_text_helper.py`:**
- Neue `clean_description_text()` Funktion (Zeilen 14-37)
- Integration in Collection-Verarbeitung (Zeile 49)

**Implementierte Funktionen:**
- `clean_description_text()`: Zentrale Funktion zur Bereinigung von Beschreibungstexten
  - Entfernt alle Arten von Zeilenwechseln (`\n`, `\r`, `\t`)
  - Normalisiert Leerzeichen und entfernt Anführungszeichen
  - Wird automatisch auf alle Collection-Beschreibungen angewendet
- `generate_description()`: Neuer API-Endpunkt mit vollständiger Fehlerbehandlung
- Intelligente JSON-Extraktion falls AI JSON statt Plain-Text zurückgibt

## [1.2.2] - 2025-01-07

### Hinzugefügt
- **Konfigurierbare Beschreibungslänge**: Neuer API-Parameter `max_description_length` (Standard: 400 Zeichen, Bereich: 50-2000) für Beschreibungstexte der Sammlungen
- **Verbesserte Beschreibungsqualität**: Implementierung hochwertiger Beschreibungstexte basierend auf detaillierten Qualitätskriterien:
  - Ansprechende, prägnante Texte die das Interesse wecken
  - Zweisätzige Struktur: Einstieg + Übersicht mit Mehrwert
  - Verständliche Sprache mit aktiven Formulierungen
  - Kurze Sätze (max. 20 Wörter) und einfache Wörter (2-3 Silben)
  - Zielgruppenanpassung für Lehrende und Lernende
  - Integration relevanter Schlüsselbegriffe
  - **Stilverbesserung**: Vermeidung repetitiver Phrasen wie "Diese Sammlung...", "Dieses Thema..." zugunsten inhaltsfokussierter Formulierungen

### Geändert
- **BASE_INSTRUCTIONS erweitert**: Vollständige Integration der detaillierten Beschreibungsanforderungen in die zentralen Formatierungsregeln
- **Prompt-Templates optimiert**: Alle Templates (MAIN, SUB, LP) referenzieren jetzt BASE_INSTRUCTIONS und integrieren konfigurierbare Parameter
- **API-Dokumentation**: Erweiterte Beschreibung der neuen Features und Parameter

### Technische Details

#### Geänderte Dateien

**`src/DTOs/topic_tree_request.py`:**
- Hinzufügung `max_description_length` Parameter (Zeilen 50-58)

**`src/prompts.py`:**
- Vollständige Überarbeitung der BASE_INSTRUCTIONS (Zeilen 17-40)
- Stilverbesserung: Vermeidung repetitiver Phrasen (Zeile 34)
- Optimierung aller Prompt-Templates (MAIN, SUB, LP) zur Referenzierung der BASE_INSTRUCTIONS

**`main.py`:**
- **Kontext-Informationen für AI-Prompts (Zeilen 219-230):**
  ```python
  # 2a) Kontext-Informationen für Fach und Bildungsstufe hinzufügen
  context_info = []
  if topic_tree_request.discipline_uri:
      context_info.append(f"Fachbereich-URIs: {', '.join(topic_tree_request.discipline_uri)}")
  if topic_tree_request.educational_context_uri:
      context_info.append(f"Bildungsstufe-URIs: {', '.join(topic_tree_request.educational_context_uri)}")
  context_instructions = (
      f"Kontext-Informationen:\n{chr(10).join(context_info)}" if context_info else ""
  )
  ```
- Integration `max_description_length` Parameter in alle Prompt-Aufrufe (Zeilen 204, 222, 240)

## [1.2.1] - 2025-01-07

### Behoben
- **Kritischer Metadaten-Bug**: URIs für Bildungsstufe (`educational_context_uri`) und Fach (`discipline_uri`) werden jetzt korrekt in die JSON-Ausgabe aller Collections und Subcollections übertragen
  
  **Problem-Analyse:**
  - **Hauptproblem**: URIs aus dem Request wurden nicht in die Properties der Collections übertragen
  - **Ursache**: Properties wurden nur mit ihren bestehenden (leeren) Werten überschrieben
  
  **Root Cause:**
  - `structured_text_helper.py` Zeilen 58, 60: Properties wurden initial mit leeren Listen für `ccm_educationalcontext` und `ccm_taxonid` erstellt
  - `main.py` Zeilen 258-280: Properties wurden nur mit ihren bestehenden (leeren) Werten überschrieben, anstatt die URIs aus dem Request zu verwenden

### Technische Details

#### Geänderte Dateien

**`main.py`:**
- **Metadaten-Bugfix - Properties-Update (Zeilen 268, 269, 277, 278, 286, 287):**
  ```python
  # Vorher (leere Arrays aus Properties):
  ccm_taxonid=main_topic.properties.ccm_taxonid,
  ccm_educationalcontext=main_topic.properties.ccm_educationalcontext,
  
  # Nachher (URIs aus Request):
  ccm_taxonid=topic_tree_request.discipline_uri or [],
  ccm_educationalcontext=topic_tree_request.educational_context_uri or [],
  ```

## [1.2.0] - Letzter offizieller Stand der API am 07.08.2025

- Grundlegende Themenbaumgenerierung mit Haupt-, Unter- und Lehrplanthemen

