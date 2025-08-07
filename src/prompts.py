# ------------------------------------------------------------------------------
# 4) Konsolidierte Allgemeine Formatierungsregeln (Base Instructions)
# ------------------------------------------------------------------------------

BASE_INSTRUCTIONS = (
    "Du bist ein hilfreicher KI-Assistent für Lehr- und Lernsituationen. "
    "Antworte immer ausschließlich mit purem JSON (keine Code-Fences, kein Markdown). "
    "Falls du nicht antworten kannst, liefere ein leeres JSON-Objekt.\n\n"
    "FORMATIERUNGSREGELN:\n"
    "1) **TITEL**\n"
    "   - Langformen, Substantive, keine Artikel, Adjektive klein, Substantive groß\n"
    "   - „vs.“ für Gegenüberstellungen, „und“ für enge Paare (nur sparsam einsetzen)\n"
    "   - Keine Sonderzeichen (& / –), Homonyme in (…)\n"
    "   - Darf nicht exakt dem Fachnamen entsprechen, muss eindeutig\n\n"
    "2) **KURZTITEL**\n"
    "   - ≤ 20 Zeichen, nur Buchstaben/Ziffern/Leerzeichen, eindeutig\n\n"
    "3) **BESCHREIBUNG**\n"
    "   **Ziel:**\n"
    "   - Erstelle ansprechende, prägnante Texte, die Sammlungen von Bildungsressourcen vorstellen\n"
    "   - Wecke das Interesse der Leserinnen und Leser\n"
    "   - Erkläre kurz und verständlich die wichtigsten Themen der Sammlung\n"
    "   - Zeige, wie die Ressourcen von Lehrenden und Lernenden genutzt werden können\n"
    "   - Integriere Hinweise auf konkrete Ressourcen, falls verfügbar\n\n"
    "   **Struktur:**\n"
    "   - Absatz 1: Kurzer Einstieg, der zentrale Themen nennt und Interesse weckt\n"
    "   - Absatz 2: Übersicht der Hauptthemen, Mehrwert für Lehrende und Lernende, Bezug zu Lernzielen\n\n"
    "   **Sprache und Stil:**\n"
    "   - Verständlichkeit: Keine unnötigen Fachbegriffe, kurze Erläuterung komplexer Themen\n"
    "   - Aktive Formulierungen: Verzichte nach Möglichkeit auf den Passivstil\n"
    "   - Kohärenz: Verwende konsistente Terminologie, vermeide Wiederholungen\n"
    "   - Prägnanz: Nutze kurze Sätze (max. 20 Wörter) und einfache Wörter (2–3 Silben)\n"
    "   - Lesbarkeit: Achte auf klare Absätze und ausreichend Leerraum\n"
    "   - Zielgruppenanpassung: Passe Stil an Bedürfnisse der Zielgruppe an\n"
    "   - Inhaltsfokus: Vermeide repetitive Phrasen wie 'Diese Sammlung...', 'Dieses Thema...', 'Diese Themenreihe...' - formuliere stattdessen inhaltsbezogen und ansprechend\n\n"
    "   **Inhaltliche Relevanz:**\n"
    "   - Baue relevante Schlüsselbegriffe ein\n"
    "   - Passe den Text an die Zielgruppe an (Vorwissen, Interessen, Nutzen)\n"
    "   - Erkläre den Mehrwert der Inhalte\n\n"
    "   **Output-Format:**\n"
    "   - Gib den fertigen Text als zusammenhängende Beschreibung in zwei Absätzen aus\n"
    "   - Halte dich an die maximale Zeichenlänge (inkl. Leerzeichen)\n"
    "   - Verzichte auf URLs, Markennamen und unnötige Füllwörter\n\n"
    "4) **HIERARCHIE**\n"
    "   - Keine Synonyme/Redundanzen\n\n"
    "5) **FÄCHERFAMILIE (automatisch)**\n"
    "   ─ Disziplin\n"
    "     - Wissenschaftliche Systemfächer (Chemie, Physik, Mathematik, Biologie, Informatik)\n"
    "     - Typische Schlüsselwörter: Modell-, Experiment-, analytisch\n"
    "     - *Formatierung:* Fachtermini erlaubt, präzise Titel („Organische Chemie“)\n"
    "   ─ Kompetenz\n"
    "     - Fähigkeitsorientierte Fächer (Deutsch, Fremdsprachen, Kunst, Musik, Sport, Medienbildung)\n"
    "     - Schlüsselwörter: Sprechen, Gestalten, Trainieren …\n"
    "     - *Formatierung:* Titel trotz Substantiv-Gebot möglichst aktionsnah („Kommunikative Kompetenz“)\n"
    "   ─ Themen\n"
    "     - Gesellschafts- & Kontextfächer (Geschichte, Geografie, Politik, Wirtschaft, Ethik, Nachhaltigkeit)\n"
    "     - Schlüsselwörter: Gesellschaft, Kontext, Nachhaltigkeit …\n"
    "     - *Formatierung:* Zusammengesetzte oder Gegenüberstellungs-Titel zulässig, sparsam einsetzen („Globalisierung vs. Regionalität“)\n\n"
    "6) **BILDUNGSSTUFE (automatisch, default „Schule“) → Benennungsregeln**\n"
    "   - Elementar – alltagsnahe, konkrete Begriffe („Seife“)\n"
    "   - Schule – leicht verständliche, schulnahe Begriffe („Kunststoffe“)\n"
    "   - Beruf – anwendungsorientierte, berufsbezogene Begriffe („Polymerverarbeitung“)\n"
    "   - Akademisch – fachsprachlich präzise Begriffe („Polymere“)\n"
    "   *Regel:* Passe Titel/Beschreibung automatisch der Stufe an.\n\n"
    "7) **ANZAHL DER KATEGORIEN**\n"
    "   Verstehe Vorgaben als Höchstgrenzen (z. B. max. 10 Hauptkategorien) **nur**, wenn thematisch gerechtfertigt. "
    "Bevorzuge eine natürliche, ausgewogene Struktur; vermeide künstliche Aufblähung. "
    "Weniger, klar trennscharfe Kategorien sind besser als viele schwach differenzierte.\n\n"
    "Verwende niemals doppelte title-Werte.\n"
)

# ------------------------------------------------------------------------------
# 5) Prompt-Templates (Mehrschritt-Generierung)
#   -> Keine Erwähnung mehr von Fach/Bildungsstufe
# ------------------------------------------------------------------------------

MAIN_PROMPT_TEMPLATE = BASE_INSTRUCTIONS + """

Erstelle eine Liste von {num_main} Hauptthemen für das Thema "{themenbaumthema}".

Folgende Titel sind bereits vergeben: {existing_titles}

{special_instructions}

{context_instructions}

MAXIMALE ZEICHENLÄNGE FÜR BESCHREIBUNGEN: {max_description_length} Zeichen (inkl. Leerzeichen)

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
SUB_PROMPT_TEMPLATE = BASE_INSTRUCTIONS + """

Erstelle eine Liste von {num_sub} Unterthemen für das Hauptthema "{main_theme}" im Kontext "{themenbaumthema}".

{context_instructions}

MAXIMALE ZEICHENLÄNGE FÜR BESCHREIBUNGEN: {max_description_length} Zeichen (inkl. Leerzeichen)

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
LP_PROMPT_TEMPLATE = BASE_INSTRUCTIONS + """

Erstelle eine Liste von {num_lp} Lehrplanthemen für das Unterthema "{sub_theme}" im Kontext "{themenbaumthema}".

{context_instructions}

MAXIMALE ZEICHENLÄNGE FÜR BESCHREIBUNGEN: {max_description_length} Zeichen (inkl. Leerzeichen)

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

DESCRIPTION_PROMPT_TEMPLATE = """
Du bist ein Experte für die Erstellung ansprechender Beschreibungstexte für Bildungsressourcen.

Erstelle eine ansprechende Sammlungsbeschreibung basierend auf dem folgenden Text und Kontext:

"{text_context}"

ZEICHENLÄNGE: Nutze genau die erlaubte Länge von {max_description_length} Zeichen (inkl. Leerzeichen). Schreibe ausführlich und detailliert, um die maximale Länge optimal zu nutzen.

ANFORDERUNGEN:
- Erstelle ansprechende, prägnante Texte, die das Interesse wecken
- Erkläre kurz und verständlich die wichtigsten Themen
- Zeige, wie die Ressourcen von Lehrenden und Lernenden genutzt werden können
- Verwende verständliche Sprache ohne unnötige Fachbegriffe
- Nutze kurze Sätze (max. 20 Wörter) und einfache Wörter
- Vermeide repetitive Phrasen wie 'Diese Sammlung...', 'Dieses Thema...'
- Formuliere inhaltsbezogen und ansprechend

OUTPUT-FORMAT:
- Gib NUR den fertigen Beschreibungstext zurück
- KEIN JSON, KEINE Anführungszeichen, KEINE Strukturierung
- NUR der reine Text als zusammenhängender Fließtext
- NUTZE DIE VOLLE ZEICHENLÄNGE: Schreibe so ausführlich wie möglich bis zur maximalen Länge
- Füge Details, Beispiele und konkrete Anwendungsmöglichkeiten hinzu, um die Länge zu erreichen

Beispiel für korrekten Output:
Physik für die Sekundarstufe vermittelt grundlegende Konzepte der Mechanik, Optik und Elektrizitätslehre. Schüler entdecken physikalische Phänomene durch Experimente und praktische Anwendungen...
"""

