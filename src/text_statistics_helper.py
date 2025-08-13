from typing import List, Dict, Any
from src.DTOs.collection import Collection
from src.DTOs.enhanced_response import TextStatistics


def calculate_text_statistics_for_description(description: str) -> Dict[str, int]:
    """
    Berechnet Textstatistiken für eine einzelne Beschreibung
    
    Args:
        description: Der Beschreibungstext
        
    Returns:
        Dictionary mit Zeichenanzahl, Wortanzahl und Zeichenanzahl mit Leerzeichen
    """
    if not description:
        return {
            "character_count": 0,
            "word_count": 0,
            "character_count_with_spaces": 0
        }
    
    # Zeichenanzahl ohne Leerzeichen
    character_count = len(description.replace(" ", "").replace("\n", "").replace("\t", ""))
    
    # Wortanzahl
    word_count = len(description.split())
    
    # Zeichenanzahl mit Leerzeichen
    character_count_with_spaces = len(description)
    
    return {
        "character_count": character_count,
        "word_count": word_count,
        "character_count_with_spaces": character_count_with_spaces
    }


def collect_all_descriptions_from_tree(collections: List[Collection]) -> List[str]:
    """
    Sammelt alle Beschreibungen aus dem gesamten Themenbaum (rekursiv)
    
    Args:
        collections: Liste der Collection-Objekte
        
    Returns:
        Liste aller Beschreibungstexte im Baum
    """
    descriptions = []
    
    for collection in collections:
        # Beschreibung der aktuellen Collection hinzufügen
        if collection.properties.cm_description:
            descriptions.extend(collection.properties.cm_description)
        
        # Rekursiv durch Subcollections gehen
        if collection.subcollections:
            descriptions.extend(collect_all_descriptions_from_tree(collection.subcollections))
    
    return descriptions


def calculate_overall_statistics(collections: List[Collection]) -> TextStatistics:
    """
    Berechnet Gesamtstatistiken für alle Beschreibungen im Themenbaum
    
    Args:
        collections: Liste der Collection-Objekte (Hauptthemen)
        
    Returns:
        TextStatistics-Objekt mit allen berechneten Statistiken
    """
    # Alle Beschreibungen sammeln
    all_descriptions = collect_all_descriptions_from_tree(collections)
    
    if not all_descriptions:
        return TextStatistics(
            total_descriptions=0,
            character_count_range={"min": 0, "max": 0},
            word_count_range={"min": 0, "max": 0},
            character_count_average=0.0,
            word_count_average=0.0,
            character_count_with_spaces_range={"min": 0, "max": 0},
            character_count_with_spaces_average=0.0
        )
    
    # Statistiken für jede Beschreibung berechnen
    stats_list = [calculate_text_statistics_for_description(desc) for desc in all_descriptions]
    
    # Werte extrahieren
    character_counts = [stats["character_count"] for stats in stats_list]
    word_counts = [stats["word_count"] for stats in stats_list]
    character_counts_with_spaces = [stats["character_count_with_spaces"] for stats in stats_list]
    
    # Gesamtstatistiken berechnen
    return TextStatistics(
        total_descriptions=len(all_descriptions),
        character_count_range={
            "min": min(character_counts),
            "max": max(character_counts)
        },
        word_count_range={
            "min": min(word_counts),
            "max": max(word_counts)
        },
        character_count_average=round(sum(character_counts) / len(character_counts), 2),
        word_count_average=round(sum(word_counts) / len(word_counts), 2),
        character_count_with_spaces_range={
            "min": min(character_counts_with_spaces),
            "max": max(character_counts_with_spaces)
        },
        character_count_with_spaces_average=round(sum(character_counts_with_spaces) / len(character_counts_with_spaces), 2)
    )


def add_text_statistics_to_collections(collections: List[Collection]) -> None:
    """
    Fügt Textstatistiken zu allen Collections im Baum hinzu (rekursiv, in-place)
    
    Args:
        collections: Liste der Collection-Objekte
    """
    for collection in collections:
        # Statistiken für die aktuelle Collection berechnen
        if collection.properties.cm_description:
            # Nehme die erste (und normalerweise einzige) Beschreibung
            description = collection.properties.cm_description[0] if collection.properties.cm_description else ""
            collection.properties.text_statistics = calculate_text_statistics_for_description(description)
        else:
            collection.properties.text_statistics = calculate_text_statistics_for_description("")
        
        # Rekursiv durch Subcollections gehen
        if collection.subcollections:
            add_text_statistics_to_collections(collection.subcollections)
