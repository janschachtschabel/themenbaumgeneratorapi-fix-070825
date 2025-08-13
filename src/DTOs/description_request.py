from pydantic import BaseModel, Field


class DescriptionRequest(BaseModel):
    """
    Request-Model für die Generierung von Sammlungsbeschreibungen.
    """

    text_context: str = Field(
        ...,
        description="Text und Kontext für die Beschreibung (z.B. Thema, Zielgruppe, Inhalte)",
        examples=[
            "Physik für die Sekundarstufe I: Mechanik, Optik und Elektrizitätslehre für Schüler der 7.-10. Klasse"
        ],
    )

    max_description_length: int = Field(
        60,
        ge=40,
        le=200,
        description="Maximale Wortanzahl für die Beschreibung (Default: 70, Bereich: 40-200)",
        examples=[60, 40, 200],
    )

    model: str = Field(
        "gpt-4.1-mini",
        description="Das zu nutzende OpenAI-Modell für die Textgenerierung",
        examples=["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text_context": "Mathematik für die Grundschule: Zahlenraum bis 100, "
                "Grundrechenarten und geometrische Formen für Klasse 1-4",
                "max_description_length": 70,
                "model": "gpt-4.1-mini",
            }
        }
