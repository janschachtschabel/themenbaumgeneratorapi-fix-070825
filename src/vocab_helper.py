from loguru import logger
from rdflib import Graph, SKOS


def _fetch_vocab(url: str) -> Graph:
    """
    Parse a SKOS vocab from a given URL.

    :param url: URL of the vocab.
        e.g.: https://vocabs.openeduhub.de/w3id.org/openeduhub/vocabs/educationalContext/index.json
    :return: `rdflib.Graph` object.
    """
    g = Graph()
    logger.debug(f"Fetching vocab from {url}")
    g.parse(url)
    return g


def _build_pref_label_dict_from_vocab_graph(graph: Graph) -> dict:
    """
    Helper function to build a dictionary of prefLabel strings for a given SKOS vocab.
    """
    _result: dict[str, list[str]] = {}
    # the final dictionary will have the vocab's "id" as its key
    # and a list of prefLabel strings as its value.
    for subject in graph.subjects(predicate=SKOS.prefLabel, object=None):
        # iterating through the subjects in this way will ONLY return the German (lang="de") values.
        # this is okay for our use case, since the OpenAI prompt only uses German terms anyway.
        _value = graph.value(subject=subject, predicate=SKOS.prefLabel)
        # typecasting the Literal object to a string is necessary (since we don't want
        _value_str: str = str(_value)  # example: "Elementarbereich"
        # _value_incl_lang = _value.n3()  # example: ""Elementarbereich"@de"
        _subject_str: str = str(subject)
        if _subject_str in _result:
            _previous = set(_result.get(_subject_str))
            _previous.add(_value_str)
            _previous_list = list(_previous)
            _result.update(
                {
                    _subject_str: _previous_list,
                }
            )
            pass
        else:
            _result.update(
                {
                    _subject_str: [_value_str],
                }
            )
        pass
    return _result


def build_vocab_cache(vocab_url: str) -> dict:
    vocab_graph = _fetch_vocab(vocab_url)
    vocab_dict = _build_pref_label_dict_from_vocab_graph(vocab_graph)
    return vocab_dict


EDU_CONTEXT_CACHE = build_vocab_cache(
    "https://vocabs.openeduhub.de/w3id.org/openeduhub/vocabs/educationalContext/index.json"
)
DISCIPLINE_CACHE = build_vocab_cache("https://vocabs.openeduhub.de/w3id.org/openeduhub/vocabs/discipline/index.json")


def get_educational_context_pref_labels(educational_context_id_uri: str) -> list[str] | None:
    if educational_context_id_uri in EDU_CONTEXT_CACHE:
        _pref_labels: list[str] = EDU_CONTEXT_CACHE.get(educational_context_id_uri)
        return _pref_labels
    else:
        return None


def get_discipline_pref_labels(discipline_id_uri: str) -> list[str] | None:
    if discipline_id_uri in DISCIPLINE_CACHE:
        _pref_labels: list[str] = DISCIPLINE_CACHE.get(discipline_id_uri)
        return _pref_labels
    else:
        return None


if __name__ == "__main__":
    logger.info(f"EDU_CONTEXT_CACHE length: {len(EDU_CONTEXT_CACHE)}")
    logger.info(f"DISCIPLINE_CACHE length: {len(DISCIPLINE_CACHE)}")
    pass
