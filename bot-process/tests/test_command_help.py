import pytest
from commands import Command
from commands.command_help import CommandHelp
from parsed_message import ParsedMessage
from language_yaml_parser import REQUEST_TYPE_TO_DESCRIPTION, REQUEST_TYPE_TO_WORDS
from request_types import RequestType


@pytest.mark.parametrize("language", list(REQUEST_TYPE_TO_DESCRIPTION.keys()))
def test_format_reply_contains_own_language_descriptions(language):
    parsed_message = ParsedMessage("", {}, {}, {})
    parsed_message.language = language
    command = CommandHelp(parsed_message)
    reply = command.format_reply(None)
    for request_type in RequestType:
        description = REQUEST_TYPE_TO_DESCRIPTION[language].get(request_type)
        if description is None:
            continue
        assert description in reply
    for other_language, other_map in REQUEST_TYPE_TO_DESCRIPTION.items():
        if other_language == language:
            continue
        for request_type, other_description in other_map.items():
            own_description = REQUEST_TYPE_TO_DESCRIPTION[language].get(request_type)
            if (not other_description) or (other_description == own_description):
                continue
            assert other_description not in reply

@pytest.mark.parametrize("language", list(REQUEST_TYPE_TO_DESCRIPTION.keys()))
def test_no_descriptionless_commands(language):
    parsed_message = ParsedMessage("", {}, {}, {})
    parsed_message.language = language
    command = CommandHelp(parsed_message)
    reply = command.format_reply(None)
    for request_type in RequestType:
        if request_type in REQUEST_TYPE_TO_DESCRIPTION[language]:
            continue
        assert all(word not in reply for word in REQUEST_TYPE_TO_WORDS[language].get(request_type, []))