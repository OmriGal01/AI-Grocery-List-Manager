import pytest
from parsed_message import ParsedMessage
from language_yaml_parser import FLAT_WORD_TO_REQUEST_TYPE, LANG_WORD_TO_REQUEST_TYPE, FLAT_PREFIX_TO_REQUEST_TYPE, WORD_TO_LANGUAGE
from request_types import RequestType

def test_yaml_valid_request_types():
    for request_type in FLAT_WORD_TO_REQUEST_TYPE.values():
        assert isinstance(request_type, RequestType)

@pytest.mark.parametrize("text,expected_type,expected_language", [
    ("help", RequestType.HELP, "English"),
    ("עזרה", RequestType.HELP, "Hebrew"),
    ("unknown_word", RequestType.ADD, "unknown"),
])
def test_parsed_message_classification(text, expected_type, expected_language):
    parsed_message = ParsedMessage(
        text,
        word_to_request_type_map=FLAT_WORD_TO_REQUEST_TYPE,
        prefix_to_request_type_map=FLAT_PREFIX_TO_REQUEST_TYPE,
        word_to_langauge_map=WORD_TO_LANGUAGE
    )
    assert parsed_message.request_type == expected_type
    assert parsed_message.language == expected_language

def test_maps_equivalency():
    for word, language in WORD_TO_LANGUAGE.items():
        assert FLAT_WORD_TO_REQUEST_TYPE[word] == LANG_WORD_TO_REQUEST_TYPE[language][word]