from typing import override
from .command import Command
from request_types import RequestType
from language_yaml_parser import REQUEST_TYPE_TO_DESCRIPTION, REQUEST_TYPE_TO_WORDS, REQUEST_TYPE_TO_PREFIXES
import asyncpg

class CommandHelp(Command):
    REQUEST_TYPE = RequestType.HELP

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        return None

    @override
    def format_reply(self, result: object) -> str:
        help_blocks = []
        language = self.parsed_message.language
        lang_specific_request_type_to_description = REQUEST_TYPE_TO_DESCRIPTION.get(language, None)
        lang_specific_request_type_to_words = REQUEST_TYPE_TO_WORDS.get(language, None)
        lang_specific_request_type_to_prefixes = REQUEST_TYPE_TO_PREFIXES.get(language, None)
        if lang_specific_request_type_to_description:
            for request_type in RequestType:
                description = lang_specific_request_type_to_description.get(request_type)
                if not description:
                    continue
                commands_and_prefixes = "/".join((lang_specific_request_type_to_words.get(request_type, [])
                                                  + lang_specific_request_type_to_prefixes.get(request_type, [])))
                block = f"{commands_and_prefixes} {description}"
                help_blocks.append(block)
            help_str = "\n\n".join(help_blocks)
            return help_str
        return "Nothing here yet!"