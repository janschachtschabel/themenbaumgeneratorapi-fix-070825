import asyncio
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from loguru import logger
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from src.DTOs.collection import Collection
from src.DTOs.description_request import DescriptionRequest
from src.DTOs.enhanced_response import EnhancedTopicTreeResponse, GenerationMetadata
from src.DTOs.ping import Ping
from src.DTOs.properties import Properties
from src.DTOs.topic_tree_request import TopicTreeRequest
from src.prompts import MAIN_PROMPT_TEMPLATE, SUB_PROMPT_TEMPLATE, LP_PROMPT_TEMPLATE, DESCRIPTION_PROMPT_TEMPLATE
from src.structured_text_helper import generate_structured_text
from src.text_statistics_helper import add_text_statistics_to_collections, calculate_overall_statistics
from src.vocab_helper import get_educational_context_pref_labels, get_discipline_pref_labels

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


# Erlaubt, dass das Collection-Modell sich selbst referenziert (subcollections)
Collection.model_rebuild()
# ToDo: figure out why model_rebuild() is called here

API_VERSION = "1.2.5"

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
    version=API_VERSION,
    contact={"name": "Themenbaum Generator Support", "email": "support@example.com"},
    license_info={"name": "Proprietär", "url": "https://example.com/license"},
)
# ToDo: set (valid) contact / license information


@app.post(
    "/generate-topic-tree",
    response_model=EnhancedTopicTreeResponse,
    summary="Generiere einen Themenbaum",
    description="""
    Generiert einen strukturierten Themenbaum basierend auf den übergebenen Parametern.

    Der Themenbaum wird in folgender Hierarchie erstellt:
    1. Hauptthemen (z.B. "Mechanik", "Thermodynamik")
    2. Unterthemen (z.B. "Kinematik", "Dynamik")
    3. Lehrplanthemen (z.B. "Gleichförmige Bewegung", "Newtonsche Gesetze")

    Jeder Knoten im Themenbaum enthält:
    - Titel und Kurztitel
    - Beschreibung
    - Schlagworte (Keywords)
    - Standardisierte Metadaten (Properties)

    Optional können URIs für Fach und Bildungsstufe übergeben werden (via ``discipline_uri`` und ``educational_context_uri``). 
    Die URIs von Fach und Bildungsstufe werden als Metadaten in die Collections eingebettet und fließen als Kontext in die AI-Prompts ein.
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
                            "version": API_VERSION,
                            "author": "Themenbaum Generator",
                        },
                        "collection": [
                            {
                                "title": "Allgemeines",
                                "shorttitle": "Allg",
                                "properties": {
                                    "cclom:general_keyword": ["physik", "grundlagen", "sekundarstufe"],
                                    "ccm:collectionshorttitle": ["Mechanik"],
                                    "ccm:educationalcontext": [
                                        "http://w3id.org/openeduhub/vocabs/educationalContext/sekundarstufe_2"
                                    ],
                                    "ccm:educationalintendedenduserrole": [
                                        "http://w3id.org/openeduhub/vocabs/intendedEndUserRole/teacher"
                                    ],
                                    "ccm:taxonid": ["http://w3id.org/openeduhub/vocabs/discipline/460"],
                                    "cm:description": [
                                        "Mechanische Bewegungen und Kräfte bilden das Fundament der Physik. Schüler entdecken die Gesetze der Kinematik und Dynamik durch praktische Experimente und mathematische Modelle."
                                    ],
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
    - ``max_description_length``: Maximale Anzahl von Wörtern für Beschreibungstexte (Default: 70, Bereich: 40-200)
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

        # 2a)
        context_info = []
        if topic_tree_request.discipline_uri:
            context_info.append(f"Fachbereich-URIs: {', '.join(topic_tree_request.discipline_uri)}")
            if isinstance(topic_tree_request.discipline_uri, list):
                _discipline_set = set()
                for _discipline_uri in topic_tree_request.discipline_uri:  # type: str
                    _discipline_pref_labels = get_discipline_pref_labels(_discipline_uri)
                    if _discipline_pref_labels:
                        _discipline_set.update(_discipline_pref_labels)
                if _discipline_set:
                    context_info.append(f"Fachbereich: {list(_discipline_set)}")
        if topic_tree_request.educational_context_uri:
            context_info.append(f"Bildungsstufe-URIs: {', '.join(topic_tree_request.educational_context_uri)}")
            if isinstance(topic_tree_request.educational_context_uri, list):
                _edu_context_set = set()
                for _uri in topic_tree_request.educational_context_uri:  # type: str
                    # example _uri value: "http://w3id.org/openeduhub/vocabs/educationalContext/sekundarstufe_1"
                    _edu_context_pref_labels = get_educational_context_pref_labels(_uri)
                    if _edu_context_pref_labels:
                        _edu_context_set.update(_edu_context_pref_labels)
                if _edu_context_set:
                    context_info.append(f"Zielgruppe / Bildungsstufe: {list(_edu_context_set)}")
        context_instructions = f"Kontext-Informationen:\n{'\n'.join(context_info)}" if context_info else ""

        logger.info(f"Generating {topic_tree_request.num_main_topics} main topics ('Hauptthemen') ...")

        # 3) Hauptthemen generieren
        main_topics = await generate_structured_text(
            client=client,
            prompt=MAIN_PROMPT_TEMPLATE.format(
                themenbaumthema=topic_tree_request.theme,
                num_main=topic_tree_request.num_main_topics,
                special_instructions=special_instructions,
                context_instructions=context_instructions,
                max_description_length=topic_tree_request.max_description_length,
            ),
            model=topic_tree_request.model,
        )
        # ToDo: extend generate_structured_text() function to include context_instructions

        if not main_topics:
            raise HTTPException(status_code=500, detail="Fehler bei der Generierung der Hauptthemen")

        logger.info("Received main topics ('Hauptthemen'). Beginning generation of sub topics ('Unterthemen') next.")

        # 4) Für jedes Hauptthema die Unterthemen generieren
        # 4a) Erstelle Liste der existierenden Hauptthemen für Kontext
        existing_main_topics_list = [f"- {topic.title}" for topic in main_topics]
        existing_main_topics_formatted = "\n".join(existing_main_topics_list) if existing_main_topics_list else "Keine weiteren Hauptthemen vorhanden."
        
        sub_topic_tasks = []
        for main_topic in main_topics:
            logger.info(f"Creating subtopic ('Unterthemen') task for '{main_topic.title}'")
            _subtopic_prompt = SUB_PROMPT_TEMPLATE.format(
                themenbaumthema=topic_tree_request.theme,
                main_theme=main_topic.title,
                num_sub=topic_tree_request.num_subtopics,
                context_instructions=context_instructions,
                existing_main_topics=existing_main_topics_formatted,
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
            # 5a) Erstelle Liste der existierenden Unterthemen für Kontext
            existing_subtopics_list = [f"- {subtopic.title}" for subtopic in main_topic.subcollections]
            existing_subtopics_formatted = "\n".join(existing_subtopics_list) if existing_subtopics_list else "Keine weiteren Unterthemen vorhanden."
            
            for sub_topic in main_topic.subcollections:
                logger.info(f"Generating curriculum ('Lehrplan') task for '{sub_topic.title}'")
                _lp_prompt = LP_PROMPT_TEMPLATE.format(
                    themenbaumthema=topic_tree_request.theme,
                    main_theme=main_topic.title,
                    sub_theme=sub_topic.title,
                    num_lp=topic_tree_request.num_curriculum_topics,
                    context_instructions=context_instructions,
                    existing_main_topics=existing_main_topics_formatted,
                    existing_subtopics=existing_subtopics_formatted,
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

        # 7) Textstatistiken zu allen Collections hinzufügen
        add_text_statistics_to_collections(main_topics)
        
        # 8) Gesamtstatistiken berechnen
        overall_statistics = calculate_overall_statistics(main_topics)
        
        # 9) Metadaten für die Generierung erstellen
        generation_metadata = GenerationMetadata(
            theme=topic_tree_request.theme,
            model=topic_tree_request.model,
            num_main_topics=topic_tree_request.num_main_topics,
            num_subtopics=topic_tree_request.num_subtopics,
            num_curriculum_topics=topic_tree_request.num_curriculum_topics,
            max_description_length=topic_tree_request.max_description_length,
            include_general_topic=topic_tree_request.include_general_topic,
            include_methodology_topic=topic_tree_request.include_methodology_topic,
            discipline_uris=topic_tree_request.discipline_uri or [],
            educational_context_uris=topic_tree_request.educational_context_uri or []
        )
        
        # 10) Finale erweiterte Antwort strukturieren
        enhanced_response = EnhancedTopicTreeResponse(
            metadata=generation_metadata,
            topic_tree=main_topics,
            statistics=overall_statistics
        )
        
        return enhanced_response

    except Exception as e:
        logger.error(f"Unhandled Exception occured while generating topic tree: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Generierung: {str(e)}")


@app.post(
    path="/generate-collection-description",
    response_model=str,
    tags=["Sammlungsbeschreibungen generieren"],
    description="""
    Generiert eine ansprechende Beschreibung für eine Sammlung von Bildungsressourcen
    basierend auf gegebenem Text und Kontext.
    
    **Parameter:**
    - `max_description_length`: Maximale Anzahl von Wörtern für Beschreibungstexte (Default: 70, Bereich: 40-200)
    - `model`: OpenAI-Modell (Default: gpt-4o-mini)
    - `text_context`: Text und Kontext für die Beschreibung (z.B. Thema, Zielgruppe, Inhalte)
    """,
)
async def generate_collection_description(description_request: DescriptionRequest) -> str:
    """
    Generiert eine ansprechende Sammlungsbeschreibung basierend auf gegebenem Text und Kontext.

    :param description_request: Request mit text_content, max_description_length und model parameter
    :return: Generierter Beschreibungstext als `str`
    :raises HTTPException: Falls ein Fehler bei der Generierung aufgetreten ist
    """
    logger.info(f"Generating collection description for '{description_request.text_context}' ...")

    # fetch OpenAI API Key from .env file
    openai_key = get_openai_key()
    if not openai_key:
        raise HTTPException(status_code=500, detail="OpenAI API Key nicht gefunden")
    # init the OpenAI client
    try:
        client = AsyncOpenAI(api_key=openai_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI-Init-Fehler: {str(e)}")

    try:
        # prepare the OpenAI prompt with the given parameters
        formatted_prompt = DESCRIPTION_PROMPT_TEMPLATE.format(
            text_context=description_request.text_context,
            max_description_length=description_request.max_description_length,
        )
        # ToDo: the "AI" generally ignores the max_description_length parameter
        #  because it has no concept of character length and does not count characters.
        # see: https://help.openai.com/en/articles/5072518-controlling-the-length-of-openai-model-responses
        # GPT-5 offers "verbosity"-settings, which might be a solution
        _system_prompt: ChatCompletionSystemMessageParam = ChatCompletionSystemMessageParam(
            content="Du bist ein Experte für die Erstellung ansprechender Beschreibungstexte für Bildungsressourcen. "
            "Antworte IMMER nur mit dem reinen Beschreibungstext. "
            "NIEMALS mit JSON, Strukturen oder Anführungszeichen. NUR der reine Text. "
            "WICHTIG: Nutze die VOLLSTÄNDIGE erlaubte Zeichenlänge - "
            "schreibe ausführlich und detailliert bis zum Maximum.",
            role="system",
        )
        _user_prompt: ChatCompletionUserMessageParam = ChatCompletionUserMessageParam(
            content=formatted_prompt,
            role="user",
        )
        _ts_before: datetime = datetime.now()
        response = await client.chat.completions.create(
            model=description_request.model,
            messages=[
                _system_prompt,
                _user_prompt,
            ],
            # temperature=0.7,
        )
        # attention: setting the `max_token`-Parameter causes the API to return more text than requested.
        # e.g.: when setting a max_token limit of 600 while also using a max_description_length of 200,
        # it will rarely result in a response within the 200-char limit!

        _ts_after: datetime = datetime.now()
        _delta: timedelta = _ts_after - _ts_before
        logger.debug(f"OpenAI-API-Call took {_delta.total_seconds()} seconds.")

        _description = response.choices[0].message.content
        return _description
    except Exception as e:
        logger.error(f"Error while generating collection description: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Generierung: {str(e)}")


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
