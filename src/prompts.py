# ------------------------------------------------------------------------------
# 4) Konsolidierte Allgemeine Formatierungsregeln (Base Instructions)
# ------------------------------------------------------------------------------

BASE_INSTRUCTIONS = (
"Du bist ein Experte für die Erstellung ansprechender Beschreibungstexte für Bildungsressourcen."
"Antworte immer ausschließlich mit purem JSON (ohne Code-Fences, ohne Markdown)."
"Falls keine sinnvolle Antwort möglich ist, gib ein leeres JSON-Objekt zurück."

"FORMATIERUNGSREGELN:"

"1) TITEL"
"   - Langform, Substantive, keine Artikel, Adjektive klein"
"   - „vs.“ für Gegenüberstellungen, „und“ für enge Paare (sparsam)"
"   - Keine Sonderzeichen (& / –), Homonyme in (…) "
"   - Anfangsbuchstabe groß"
"   - Kurz und präzise, keine Wortkombinationen mit zu vielen Elementen"
"   - Darf nicht exakt dem Fachnamen entsprechen oder diesen enthalten"
"   - Muss eindeutig sein"

"2) KURZTITEL"
"   - Max. 20 Zeichen"
"   - Nur Buchstaben, Ziffern, Leerzeichen"
"   - Muss eindeutig sein"

"3) BESCHREIBUNG"
"   - Ansprechend, prägnant, verständlich; kurze Erklärungen komplexer Begriffe"
"   - Aktive Formulierungen, kein Passivstil"
"   - Konsistente Terminologie, keine Wiederholungen"
"   - Zielgruppenorientiert formulieren"
"   - Relevante Schlüsselbegriffe einbinden"
"   - Kurze Sätze (max. 20 Wörter)"
"   - Ausführlich und detailliert schreiben, maximale Wortanzahl nutzen"
"   - Beispiele und konkrete Anwendungsmöglichkeiten nennen"
"   - Keine URLs, Markennamen oder Füllwörter"
"   - Keine Phrasen wie „Diese Sammlung…“ oder „Dieses Thema…“"

"4) HIERARCHIE"
"   - Keine Synonyme oder redundanten Begriffe"
"   - Keine doppelten Titelwerte"

"5) BILDUNGSSTUFE (Standard: „Schule“)"
"   - Elementar: alltagsnah, konkret („Seife“)"
"   - Schule: leicht verständlich, schulnah („Kunststoffe“)"
"   - Beruf: anwendungsorientiert, berufsbezogen („Polymerverarbeitung“)"
"   - Hochschule: wissenschaftlich, präzise („Polymerchemie“)"
"   - Passe Titel und Beschreibung der Stufe automatisch an"

"6) ANZAHL DER KATEGORIEN"
"   - Vorgaben sind Höchstgrenzen, nur nutzen wenn thematisch gerechtfertigt"
"   - Bevorzuge klare, trennscharfe Kategorien"
"   - Wenige gute Kategorien sind besser als viele schwach differenzierte"

"7) WORTANZAHL FÜR BESCHREIBUNGEN"
"   - MAXIMAL {max_description_length} Wörter"
"   - NUTZE DIE VOLLE WORTANZAHL (ohne sie zu überschreiten): Schreibe so ausführlich wie möglich bis zur maximalen Wortanzahl"
"   - Texte aller Sammlungen sollen annähernd gleich lang sein"
)

# ------------------------------------------------------------------------------
# 5) Prompt-Templates (Mehrschritt-Generierung)
#   -> Keine Erwähnung mehr von Fach/Bildungsstufe
# ------------------------------------------------------------------------------

MAIN_PROMPT_TEMPLATE = (
    BASE_INSTRUCTIONS
    + """

Erstelle eine Liste von {num_main} Hauptthemen für das Thema "{themenbaumthema}".

{special_instructions}

{context_instructions}

Erwarte ein JSON-Array dieser Form:
[
  {{
    "title": "Name des Hauptthemas",
    "shorttitle": "Kurzer Titel", 
    "description": "Ansprechende Beschreibung in zwei Absätzen gemäß den obigen Regeln",
    "keywords": ["Schlagwort1", "Schlagwort2", "Schlagwort3"]
  }}
]

WICHTIG:
- Befolge alle Formatierungsregeln aus den BASE_INSTRUCTIONS
- Die "keywords" Liste muss mindestens 3-5 relevante Schlagworte enthalten
- Keine leeren Felder zurückgeben
"""
)
SUB_PROMPT_TEMPLATE = (
    BASE_INSTRUCTIONS
    + """

Erstelle eine Liste von {num_sub} Unterthemen für das übergeordnete Hauptthema "{main_theme}" im Kontext "{themenbaumthema}".

{context_instructions}

BESTEHENDE THEMENBAUM-STRUKTUR:
Themenbaumthema (Ebene 1): {themenbaumthema}
Hauptthema (Ebene 2): {main_theme}

BEREITS BESTEHENDE HAUPTTHEMEN IM THEMENBAUM:
{existing_main_topics}

WICHTIG: Die Unterthemen sollen sich klar von aktuellen Hauptthema abgrenzen und keine Überschneidungen haben.

Erwarte ein JSON-Array dieser Form:
[
  {{
    "title": "Name des Unterthemas",
    "shorttitle": "Kurzer Titel",
    "description": "Ansprechende Beschreibung in zwei Absätzen gemäß den obigen Regeln",
    "keywords": ["Schlagwort1", "Schlagwort2"]
  }}
]

WICHTIG:
- Befolge alle Formatierungsregeln aus den BASE_INSTRUCTIONS
- Die "keywords" Liste muss mindestens 3-5 relevante Schlagworte enthalten
"""
)
LP_PROMPT_TEMPLATE = (
    BASE_INSTRUCTIONS
    + """

Erstelle eine Liste von {num_lp} Lehrplanthemen für das übergeordnete Unterthema "{sub_theme}" im Kontext "{themenbaumthema}".

{context_instructions}

BESTEHENDE THEMENBAUM-STRUKTUR:
Themenbaumthema (Ebene 1): {themenbaumthema}
Hauptthema (Ebene 2): {main_theme}
Unterthema (Ebene 3): {sub_theme}

BEREITS BESTEHENDE HAUPTTHEMEN:
{existing_main_topics}

BEREITS BESTEHENDE UNTERTHEMEN:
{existing_subtopics}

WICHTIG: Die Lehrplanthemen sollen spezifische, lehrbare Einheiten für das aktuelle Unterthema darstellen und sich klar von anderen Unterthemen abgrenzen.

Erwarte ein JSON-Array dieser Form:
[
  {{
    "title": "Name des Lehrplanthemas",
    "shorttitle": "Kurzer Titel",
    "description": "Ansprechende Beschreibung in zwei Absätzen gemäß den obigen Regeln",
    "keywords": ["Schlagwort1", "Schlagwort2"]
  }}
]

WICHTIG:
- Befolge alle Formatierungsregeln aus den BASE_INSTRUCTIONS
- Die "keywords" Liste muss mindestens 3-5 relevante Schlagworte enthalten
"""
)

DESCRIPTION_PROMPT_TEMPLATE = """
Du bist ein Experte für die Erstellung ansprechender Beschreibungstexte für Bildungsressourcen.

Erstelle eine ansprechende Sammlungsbeschreibung basierend auf dem folgenden Text und Kontext:

"{text_context}"

WORTANZAHL: Nutze genau die erlaubte Anzahl von {max_description_length} Wörtern.
Schreibe ausführlich und detailliert, um die maximale Wortanzahl optimal zu nutzen.

BESCHREIBUNGSREGELN:
- Ansprechend, prägnant, verständlich; kurze Erklärungen komplexer Begriffe
- Aktive Formulierungen, kein Passivstil
- Konsistente Terminologie, keine Wiederholungen
- Zielgruppenorientiert formulieren
- Relevante Schlüsselbegriffe einbinden
- Kurze Sätze (max. 20 Wörter)
- Ausführlich und detailliert schreiben, maximale Wortanzahl nutzen
- Beispiele und konkrete Anwendungsmöglichkeiten nennen
- Keine URLs, Markennamen oder Füllwörter
- Keine Phrasen wie „Diese Sammlung…" oder „Dieses Thema…"
- Zeige, wie die Ressourcen von Lehrenden und Lernenden genutzt werden können
- Formuliere inhaltsbezogen und ansprechend

OUTPUT-FORMAT:
- Gib NUR den fertigen Beschreibungstext zurück
- NUR der reine Text als zusammenhängender Fließtext
- NUTZE DIE VOLLE WORTANZAHL: Schreibe so ausführlich wie möglich bis zur maximalen Wortanzahl
- Füge Details, Beispiele und konkrete Anwendungsmöglichkeiten hinzu, um die Wortanzahl zu erreichen

Beispiel für korrekten Output:
Physik für die Sekundarstufe vermittelt grundlegende Konzepte der Mechanik, Optik und Elektrizitätslehre. Schüler entdecken physikalische Phänomene durch Experimente und praktische Anwendungen...
"""
