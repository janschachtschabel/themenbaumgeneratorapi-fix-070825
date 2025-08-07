from pydantic import BaseModel, Field
from typing import Optional


class DescriptionRequest(BaseModel):
    """
    Request-Modell für die Generierung von Sammlungsbeschreibungen.
    """
    
    text_context: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Text und Kontext für die Beschreibung (z.B. Thema, Zielgruppe, Inhalte)",
        example="Physik für die Sekundarstufe I: Mechanik, Optik und Elektrizitätslehre für Schüler der 7.-10. Klasse"
    )
    
    max_description_length: int = Field(
        400,
        ge=50,
        le=2000,
        description="Maximale Zeichenlänge für die Beschreibung (Standard: 400)",
        examples=[400, 300, 600]
    )
    
    model: str = Field(
        "gpt-4.1-mini",
        description="OpenAI-Modell für die Textgenerierung",
        examples=["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text_context": "Mathematik für die Grundschule: Zahlenraum bis 100, Grundrechenarten und geometrische Formen für Klasse 1-4",
                "max_description_length": 400,
                "model": "gpt-4.1-mini"
            }
        }
