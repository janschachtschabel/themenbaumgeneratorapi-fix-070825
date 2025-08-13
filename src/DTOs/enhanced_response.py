from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.DTOs.collection import Collection


class GenerationMetadata(BaseModel):
    """
    Metadaten für die Themenbaumgenerierung
    """
    theme: str = Field(description="Das Hauptthema des Themenbaums")
    model: str = Field(description="Verwendetes AI-Modell")
    num_main_topics: int = Field(description="Anzahl der generierten Hauptthemen")
    num_subtopics: int = Field(description="Anzahl der Unterthemen pro Hauptthema")
    num_curriculum_topics: int = Field(description="Anzahl der Lehrplanthemen pro Unterthema")
    max_description_length: int = Field(description="Maximale Wortanzahl für Beschreibungen")
    include_general_topic: bool = Field(description="Ob 'Allgemeines' Thema eingeschlossen wurde")
    include_methodology_topic: bool = Field(description="Ob 'Methodik und Didaktik' Thema eingeschlossen wurde")
    discipline_uris: List[str] = Field(default_factory=list, description="URIs der Fachbereiche")
    educational_context_uris: List[str] = Field(default_factory=list, description="URIs der Bildungsstufen")


class TextStatistics(BaseModel):
    """
    Statistiken über die Textlängen aller generierten Beschreibungen
    """
    total_descriptions: int = Field(description="Gesamtanzahl der generierten Beschreibungen")
    character_count_range: Dict[str, int] = Field(description="Min/Max Zeichenanzahl")
    word_count_range: Dict[str, int] = Field(description="Min/Max Wortanzahl")
    character_count_average: float = Field(description="Durchschnittliche Zeichenanzahl")
    word_count_average: float = Field(description="Durchschnittliche Wortanzahl")
    character_count_with_spaces_range: Dict[str, int] = Field(description="Min/Max Zeichenanzahl mit Leerzeichen")
    character_count_with_spaces_average: float = Field(description="Durchschnittliche Zeichenanzahl mit Leerzeichen")


class EnhancedTopicTreeResponse(BaseModel):
    """
    Erweiterte Antwort für die Themenbaumgenerierung mit Metadaten und Statistiken
    """
    metadata: GenerationMetadata = Field(description="Metadaten der Generierung")
    topic_tree: List[Collection] = Field(description="Der generierte Themenbaum")
    statistics: TextStatistics = Field(description="Statistiken über die generierten Texte")
