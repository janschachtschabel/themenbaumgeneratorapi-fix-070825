import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from loguru import logger
from openai import AsyncOpenAI

from src.DTOs.collection import Collection
from src.DTOs.ping import Ping
from src.DTOs.properties import Properties
from src.DTOs.topic_tree_request import TopicTreeRequest
from src.DTOs.description_request import DescriptionRequest
from src.prompts import MAIN_PROMPT_TEMPLATE, SUB_PROMPT_TEMPLATE, LP_PROMPT_TEMPLATE, DESCRIPTION_PROMPT_TEMPLATE
from src.structured_text_helper import generate_structured_text

# ToDo: replace / remove unnecessary dependencies
#  - replace "backoff" dependency since its unmaintained / abandonware
#  - replace OpenAI implementation with edu-sharing B.API
#    - define edu-sharing connector class
#  -> as of 2025-02-07 replacing the OpenAI client is no longer a priority since this prototype is intended for
#  quick iteration.

# ToDo: allow dynamic prompt updates
#  - prompts and basic instructions should allow for dynamic updates
#    - e.g. by fetching the prompt string from an edu-sharing node
#    - or via edu-sharing admin-tools

# ToDo: fix variable names and prompt placeholders
#  - either use German as our domain language for everything
#  - or properly translate everything to English

load_dotenv()


def get_openai_key():
    """Liest den OpenAI-API-Key aus den Umgebungsvariablen."""
    return os.getenv("OPENAI_API_KEY", "")


def extract_educational_context_info(educational_context_uris: list) -> str:
    """
    Extrahiert lesbare Bildungsstufen-Informationen aus URIs.
    
    Args:
        educational_context_uris: Liste von Bildungsstufen-URIs
        
    Returns:
        str: Lesbare Bildungsstufen-Information oder leerer String
        
    Beispiel:
        Input: ["http://w3id.org/openeduhub/vocabs/educationalContext/sekundarstufe_2"]
        Output: "sekundarstufe_2"
    """
    if not educational_context_uris:
        return ""
    
    readable_contexts = []
    for uri in educational_context_uris:
        # Extrahiere den letzten Teil der URI nach dem letzten '/'
        if '/' in uri:
            context_segment = uri.split('/')[-1]
            # Ersetze Unterstriche durch Leerzeichen für bessere Lesbarkeit
            readable_context = context_segment.replace('_', ' ')
            readable_contexts.append(readable_context)
        else:
            # Falls keine URI-Struktur, verwende den ganzen String
            readable_contexts.append(uri)
    
    return ', '.join(readable_contexts)


# Erlaubt, dass das Collection-Modell sich selbst referenziert (subcollections)
Collection.model_rebuild()
# ToDo: figure out why model_rebuild() is called here

# ------------------------------------------------------------------------------
# 7) FastAPI App
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Themenbaum Generator API",
    description="""
    ## Themenbaum Generator API

    Diese API ermöglicht die automatische Generierung von strukturierten Themenbäumen für Bildungsinhalte.

    ### Hauptfunktionen

    - **Themenbaumgenerierung**: Erstellt hierarchisch strukturierte Themenbäume mit Haupt-, Unter- und Lehrplanthemen
    - **Bildungskontext** (optional per URI): Falls gewünscht, kann eine Bildungsstufen-URI angegeben werden
    - **Fach (Disziplin)** (optional per URI): Falls gewünscht, kann eine Fach-URI angegeben werden
    - **Metadaten**: Generiert standardisierte Metadaten für jeden Knoten im Themenbaum

    ### Verwendung

    1. Senden Sie eine POST-Anfrage an den `/generate-topic-tree` Endpunkt
    2. Definieren Sie die gewünschten Parameter wie Thema, Anzahl der Themen und optional die URIs für Fach & Kontext
    3. Erhalten Sie einen strukturierten Themenbaum im JSON-Format

    ### Authentifizierung

    Die API verwendet einen OpenAI API-Schlüssel, der über die Umgebungsvariable `OPENAI_API_KEY` bereitgestellt werden muss.
    """,
    version="1.2.0",
    contact={"name": "Themenbaum Generator Support", "email": "support@example.com"},
    license_info={"name": "Proprietär", "url": "https://example.com/license"},
)
# ToDo: set (valid) contact / license information


@app.post(
    "/generate-topic-tree",
    response_model=dict,
    summary="Generiere einen Themenbaum",
    description="""
    Generiert einen strukturierten Themenbaum basierend auf den übergebenen Parametern.

    Der Themenbaum wird in folgender Hierarchie erstellt:
    1. Hauptthemen (z.B. "Mechanik", "Thermodynamik")
    2. Unterthemen (z.B. "Kinematik", "Dynamik")
    3. Lehrplanthemen (z.B. "Gleichförmige Bewegung", "Newtonsche Gesetze")

    Jeder Knoten im Themenbaum enthält:
    - Titel und Kurztitel
    - **Hochwertige Beschreibung** (ansprechend, prägnant, inhaltsfokussiert)
    - Schlagworte (Keywords)
    - Standardisierte Metadaten (Properties)

    **Neue Features:**
    - **Konfigurierbare Beschreibungslänge**: Parameter ``max_description_length`` (Standard: 500 Zeichen)
    - **Verbesserte Beschreibungsqualität**: Ansprechende, zielgruppengerechte Texte ohne repetitive Phrasen
    - **Metadaten-Integration**: URIs für Fach und Bildungsstufe werden korrekt in die JSON-Ausgabe übertragen

    Optional können URIs für Fach und Bildungsstufe übergeben werden (via ``discipline_uri`` und ``educational_context_uri``). 
    Diese URIs werden als Metadaten in die Collections eingebettet und fließen als Kontext in die AI-Prompts ein.
    """,
    responses={
        200: {
            "description": "Erfolgreich generierter Themenbaum",
            "content": {
                "application/json": {
                    "example": {
                        "metadata": {
                            "title": "Physik in Anlehnung an die Lehrpläne der Sekundarstufe 2",
                            "description": "Themenbaum für Physik in der Sekundarstufe II",
                            "created_at": "2025-02-05T11:28:40+01:00",
                            "version": "1.2.0",
                            "author": "Themenbaum Generator",
                        },
                        "collection": [
                            {
                                "title": "Allgemeines",
                                "shorttitle": "Allg",
                                "properties": {
                                    "cclom:general_keyword": ["physik", "grundlagen", "sekundarstufe"],
                                    "ccm:collectionshorttitle": ["Mechanik"],
                                    "ccm:educationalcontext": ["http://w3id.org/openeduhub/vocabs/educationalContext/sekundarstufe_2"],
                                    "ccm:educationalintendedenduserrole": [
                                        "http://w3id.org/openeduhub/vocabs/intendedEndUserRole/teacher"
                                    ],
                                    "ccm:taxonid": ["http://w3id.org/openeduhub/vocabs/discipline/460"],
                                    "cm:description": ["Mechanische Bewegungen und Kräfte bilden das Fundament der Physik. Schüler entdecken die Gesetze der Kinematik und Dynamik durch praktische Experimente und mathematische Modelle."],
                                    "cm:title": ["Mechanik"],
                                },
                                "subcollections": [],
                            }
                        ],
                    }
                }
            },
        },
        500: {
            "description": "Interner Serverfehler",
            "content": {"application/json": {"example": {"detail": "OpenAI API Key nicht gefunden"}}},
        },
    },
    tags=["Themenbaum-Generator"],
)
async def generate_topic_tree(topic_tree_request: TopicTreeRequest):
    """
    Generiert einen strukturierten Themenbaum basierend auf den Eingabeparametern.

    - ``theme``: Hauptthema
    - ``num_main_topics``: Anzahl der Hauptthemen (1 bis 30)
    - ``num_subtopics``: Anzahl der Unterthemen pro Hauptthema (0 bis 20)
    - ``num_curriculum_topics``: Anzahl der Lehrplanthemen pro Unterthema (0 bis 20)
    - ``include_general_topic``: Falls True, fügt ein Hauptthema "Allgemeines" hinzu
    - ``include_methodology_topic``: Falls True, fügt ein Hauptthema "Methodik und Didaktik" hinzu
    - ``max_description_length``: Maximale Zeichenlänge für Beschreibungstexte (Standard: 500, Bereich: 50-2000)
    - ``discipline_uri``: Falls übergeben, werden diese URIs in den ``ccm:taxonid``-Properties eingebettet und fließen als Kontext in die AI-Prompts ein
    - ``educational_context_uri``: Falls übergeben, werden diese URIs in den ``ccm:educationalcontext``-Properties eingebettet und fließen als Kontext in die AI-Prompts ein
    """
    logger.info(
        f"Request received. Starting OpenAI chat completion request with the following settings: {topic_tree_request}"
    )
    # 1) OpenAI-Key holen
    openai_key = get_openai_key()
    if not openai_key:
        raise HTTPException(status_code=500, detail="OpenAI API Key nicht gefunden")

    try:
        client = AsyncOpenAI(api_key=openai_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI-Init-Fehler: {str(e)}")

    try:
        # 2) Spezialanweisungen für Hauptthemen (z.B. Allgemeines, Methodik etc.)
        special_instructions = []
        if topic_tree_request.include_general_topic:
            special_instructions.append("1) Hauptthema 'Allgemeines' an erster Stelle")
        if topic_tree_request.include_methodology_topic:
            special_instructions.append("2) Hauptthema 'Methodik und Didaktik' an letzter Stelle")
        special_instructions = (
            "\n".join(special_instructions) if special_instructions else "Keine besonderen Anweisungen."
        )

        # 2a) Kontext-Informationen für Fach und Bildungsstufe hinzufügen
        context_info = []
        if topic_tree_request.discipline_uri:
            context_info.append(f"Fachbereich-URIs: {', '.join(topic_tree_request.discipline_uri)}")
        if topic_tree_request.educational_context_uri:
            # Füge sowohl URIs als auch lesbare Bildungsstufen-Info hinzu
            context_info.append(f"Bildungsstufe-URIs: {', '.join(topic_tree_request.educational_context_uri)}")
            
            # Extrahiere lesbare Bildungsstufen-Information
            readable_context = extract_educational_context_info(topic_tree_request.educational_context_uri)
            if readable_context:
                context_info.append(f"Zielgruppe/Bildungsstufe: {readable_context}")
        
        context_instructions = (
            f"Kontext-Informationen:\n{chr(10).join(context_info)}" if context_info else ""
        )

        logger.info(f"Generating {topic_tree_request.num_main_topics} main topics ('Hauptthemen') ...")

        # 3) Hauptthemen generieren
        main_topics = await generate_structured_text(
            client=client,
            prompt=MAIN_PROMPT_TEMPLATE.format(
                themenbaumthema=topic_tree_request.theme,
                num_main=topic_tree_request.num_main_topics,
                existing_titles="",
                special_instructions=special_instructions,
                context_instructions=context_instructions,
                max_description_length=topic_tree_request.max_description_length,
            ),
            model=topic_tree_request.model,
        )

        if not main_topics:
            raise HTTPException(status_code=500, detail="Fehler bei der Generierung der Hauptthemen")

        logger.info("Received main topics ('Hauptthemen'). Beginning generation of sub topics ('Unterthemen') next.")

        # 4) Für jedes Hauptthema die Unterthemen generieren
        sub_topic_tasks = []
        for main_topic in main_topics:
            logger.info(f"Creating subtopic ('Unterthemen') task for '{main_topic.title}'")
            _subtopic_prompt = SUB_PROMPT_TEMPLATE.format(
                themenbaumthema=topic_tree_request.theme,
                main_theme=main_topic.title,
                num_sub=topic_tree_request.num_subtopics,
                context_instructions=context_instructions,
                max_description_length=topic_tree_request.max_description_length,
            )
            _task = generate_structured_text(
                client=client,
                prompt=_subtopic_prompt,
                model=topic_tree_request.model,
            )
            sub_topic_tasks.append(_task)

        sub_topic_results = await asyncio.gather(*sub_topic_tasks)

        for i, main_topic in enumerate(main_topics):
            sub_topics = sub_topic_results[i]
            if sub_topics:
                main_topic.subcollections = sub_topics

        logger.info("Received subtopics ('Unterthemen'). Beginning generation of curriculum ('Lehrplan') next.")

        # 5) Für jedes Unterthema die Lehrplanthemen generieren
        lp_tasks = []
        lp_mapping = []  # List to track which main_topic and sub_topic each task corresponds to

        for main_topic in main_topics:
            for sub_topic in main_topic.subcollections:
                logger.info(f"Generating curriculum ('Lehrplan') task for '{sub_topic.title}'")
                _lp_prompt = LP_PROMPT_TEMPLATE.format(
                    themenbaumthema=topic_tree_request.theme,
                    main_theme=main_topic.title,
                    sub_theme=sub_topic.title,
                    num_lp=topic_tree_request.num_curriculum_topics,
                    context_instructions=context_instructions,
                    max_description_length=topic_tree_request.max_description_length,
                )
                _lp_task = generate_structured_text(
                    client=client,
                    prompt=_lp_prompt,
                    model=topic_tree_request.model,
                )
                lp_tasks.append(_lp_task)
                lp_mapping.append((main_topic, sub_topic))

        lp_results = await asyncio.gather(*lp_tasks)

        for i, (main_topic, sub_topic) in enumerate(lp_mapping):
            lp_topics = lp_results[i]
            if lp_topics:
                sub_topic.subcollections = lp_topics

        # 6) Properties für alle Knoten nochmal updaten mit den (ggf.) übergebenen URIs
        for main_topic in main_topics:
            main_topic.properties = Properties(
                cm_title=[main_topic.title],
                ccm_collectionshorttitle=[main_topic.shorttitle],
                cm_description=main_topic.properties.cm_description,
                cclom_general_keyword=main_topic.properties.cclom_general_keyword,
                ccm_taxonid=topic_tree_request.discipline_uri or [],
                ccm_educationalcontext=topic_tree_request.educational_context_uri or [],
            )

            for sub_topic in main_topic.subcollections:
                sub_topic.properties = Properties(
                    cm_title=[sub_topic.title],
                    ccm_collectionshorttitle=[sub_topic.shorttitle],
                    cm_description=sub_topic.properties.cm_description,
                    cclom_general_keyword=sub_topic.properties.cclom_general_keyword,
                    ccm_taxonid=topic_tree_request.discipline_uri or [],
                    ccm_educationalcontext=topic_tree_request.educational_context_uri or [],
                )

                for lp_topic in sub_topic.subcollections:
                    lp_topic.properties = Properties(
                        cm_title=[lp_topic.title],
                        ccm_collectionshorttitle=[lp_topic.shorttitle],
                        cm_description=lp_topic.properties.cm_description,
                        cclom_general_keyword=lp_topic.properties.cclom_general_keyword,
                        ccm_taxonid=topic_tree_request.discipline_uri or [],
                        ccm_educationalcontext=topic_tree_request.educational_context_uri or [],
                    )

        # 7) Finale Daten strukturieren (Metadaten + Collection-Liste)
        final_data = {
            "metadata": {
                "title": topic_tree_request.theme,
                "description": f"Themenbaum für {topic_tree_request.theme}",
                "target_audience": "Lehrkräfte",
                "created_at": datetime.now().isoformat(),
                "version": "1.2.0",
                "author": "Themenbaum Generator",
            },
            "collection": [topic.to_dict() for topic in main_topics],
        }

        # ToDo: actually return a JSON object (instead of a python dict) as soon as you're done with debugging
        return final_data

    except Exception as e:
        logger.error(f"Unhandled Exception occured while generating topic tree: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Generierung: {str(e)}")


@app.post(
    path="/generate-collection-description",
    response_model=str,
    tags=["description generation"],
    summary="Generiere Sammlungsbeschreibung",
    description="""
    Generiert eine ansprechende Beschreibung für eine Sammlung von Bildungsressourcen
    basierend auf gegebenem Text und Kontext.
    
    **Parameter:**
    - `text_context`: Text und Kontext für die Beschreibung (z.B. Thema, Zielgruppe, Inhalte)
    - `max_description_length`: Maximale Zeichenlänge (Standard: 400, Bereich: 50-2000)
    - `model`: OpenAI-Modell (Standard: gpt-4o-mini)
    
    **Rückgabe:**
    - Ansprechende Beschreibung in zwei Absätzen gemäß den Qualitätskriterien
    - Vermeidung repetitiver Phrasen
    - Inhaltsfokussierte, zielgruppengerechte Formulierung
    """,
)
async def generate_description(description_request: DescriptionRequest):
    """
    Generiert eine ansprechende Sammlungsbeschreibung basierend auf Text und Kontext.
    
    Args:
        description_request: Request mit text_context, max_description_length und model
        
    Returns:
        str: Generierte Beschreibung als reiner Text
        
    Raises:
        HTTPException: Bei Fehlern in der Generierung
    """
    try:
        logger.info(f"Generating description for context: {description_request.text_context[:100]}...")
        
        # 1) OpenAI-Key holen
        openai_key = get_openai_key()
        if not openai_key:
            raise HTTPException(status_code=500, detail="OpenAI API Key nicht gefunden")
        
        # 2) OpenAI-Client erstellen
        try:
            client = AsyncOpenAI(api_key=openai_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI-Init-Fehler: {str(e)}")
        
        # 3) Prompt mit Parametern formatieren
        formatted_prompt = DESCRIPTION_PROMPT_TEMPLATE.format(
            text_context=description_request.text_context,
            max_description_length=description_request.max_description_length
        )
        
        # 4) OpenAI API aufrufen
        response = await client.chat.completions.create(
            model=description_request.model,
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein Experte für die Erstellung ansprechender Beschreibungstexte für Bildungsressourcen. Antworte IMMER nur mit dem reinen Beschreibungstext. NIEMALS mit JSON, Strukturen oder Anführungszeichen. NUR der reine Text. WICHTIG: Nutze die VOLLSTÄNDIGE erlaubte Zeichenlänge - schreibe ausführlich und detailliert bis zum Maximum."
                },
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        description = response.choices[0].message.content.strip()
        
        # Falls JSON zurückgegeben wurde, extrahiere nur die Beschreibung
        import json
        import re
        
        try:
            # Versuche JSON zu parsen falls es JSON ist
            if description.startswith('{') and description.endswith('}'):
                json_data = json.loads(description)
                # Suche nach beschreibung/description Feld
                if 'beschreibung' in json_data:
                    description = json_data['beschreibung']
                elif 'description' in json_data:
                    description = json_data['description']
                else:
                    # Falls kein bekanntes Feld, nimm den längsten String-Wert
                    description = max([v for v in json_data.values() if isinstance(v, str)], key=len)
        except:
            # Falls JSON-Parsing fehlschlägt, verwende den ursprünglichen Text
            pass
        
        # Bereinige alle Arten von Zeilenwechseln und formatiere als sauberen Text
        description = description.replace('\\n', ' ')  # Escape-Sequenzen
        description = description.replace('\n', ' ')   # Echte Zeilenwechsel
        description = description.replace('\r', ' ')   # Carriage Returns
        description = description.replace('\t', ' ')   # Tabs
        
        # Entferne Anführungszeichen am Anfang und Ende
        description = description.strip('"\'')
        
        # Mehrfache Leerzeichen durch einzelne ersetzen
        description = re.sub(r'\s+', ' ', description).strip()
        
        logger.info(f"Successfully generated description with {len(description)} characters")
        return description
        
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Beschreibungsgenerierung: {str(e)}")


@app.get(path="/_ping", response_model=Ping, tags=["health check"])
async def ping_endpoint():
    """Ping function for Kubernetes health checks."""
    return Ping(status="ok")


@app.get(path="/", include_in_schema=False)
async def root_endpoint():
    return {
        "message": "Hi there! The API Documentation is available in two formats: "
        "Please take a look at the /docs endpoint (for the Swagger UI) - or - "
        "take a look at the /redoc endpoint for an alternative documentation (by Redoc).",
        "API docs": {"swagger": "/docs", "redoc": "/redoc"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
