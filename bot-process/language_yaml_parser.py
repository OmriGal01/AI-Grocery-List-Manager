from pathlib import Path
import yaml
from request_types import RequestType

class LanguageParser:
    def __init__(self, language_config_path: Path):
        self.language_config = yaml.safe_load(language_config_path.read_text())

    def get_flattened_commands_dicts(self) -> tuple[dict[str, RequestType], dict[str, RequestType]]:
        word_to_request_type, prefix_to_request_type = {}, {}
        for language_data in self.language_config.values():
            for word, type_name in language_data.get("words", {}).items():
                word_to_request_type[word] = RequestType[type_name]
            for prefix, type_name in language_data.get("prefixes", {}).items():
                prefix_to_request_type[prefix] = RequestType[type_name]
        return word_to_request_type, prefix_to_request_type

    def get_request_type_to_words_prefixes_dicts(self) -> tuple[dict, dict]:
        word_to_request_type, prefix_to_request_type = self.get_flattened_commands_dicts()
        return LanguageParser._get_flipped_dict(word_to_request_type), LanguageParser._get_flipped_dict(prefix_to_request_type)

    def get_descriptions(self) -> dict[RequestType, str]:
        descriptions = {}
        for language_data in self.language_config.values():
            for type_name, description in language_data.get("descriptions", {}).items():
                descriptions[RequestType[type_name]] = description
        return descriptions

    @staticmethod
    def _get_flipped_dict(dct: dict) -> dict:
        flipped_dict = {value: [] for value in dct.values()}
        for key, value in dct.items():
            flipped_dict[value].append(key)
        return flipped_dict

LANGUAGES_CONFIG_PATH = Path(__file__).resolve().parent / "languages_config.yaml"
language_parser = LanguageParser(LANGUAGES_CONFIG_PATH)
WORD_TO_REQUEST_TYPE, PREFIX_TO_REQUEST_TYPE = language_parser.get_flattened_commands_dicts()
REQUEST_TYPE_TO_DESCRIPTION = language_parser.get_descriptions()
REQUEST_TYPE_TO_WORDS, REQUEST_TYPE_TO_PREFIXES = language_parser.get_request_type_to_words_prefixes_dicts()