from pathlib import Path
import yaml
from request_types import RequestType

class LanguageParser:
    def __init__(self, language_config_path: Path):
        self.language_config = yaml.safe_load(language_config_path.read_text(encoding="utf-8"))

    def get_language_specific_maps(self) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
        language_and_word_map, language_and_prefix_map = {}, {}
        for language, language_data in self.language_config.items():
            word_to_request_type_map, prefix_to_request_type_map = {}, {}
            for word, type_name in language_data.get("words", {}).items():
                word_to_request_type_map[word] = RequestType[type_name]
            for prefix, type_name in language_data.get("prefixes", {}).items():
                prefix_to_request_type_map[prefix] = RequestType[type_name]
            language_and_word_map[language] = word_to_request_type_map
            language_and_prefix_map[language] = prefix_to_request_type_map
        return language_and_word_map, language_and_prefix_map

    def get_flattened_commands_map(self) -> tuple[dict[str, RequestType], dict[str, RequestType]]:
        language_and_word_map, language_and_prefix_map = self.get_language_specific_maps()
        flattened_words_map, flattened_prefix_map = {}, {}
        for language_data in language_and_word_map.values():
            flattened_words_map |= language_data
        for language_data in language_and_prefix_map.values():
            flattened_prefix_map |= language_data
        return flattened_words_map, flattened_prefix_map

    def get_language_specific_request_type_to_words_prefixes_maps(self) -> tuple[dict, dict]:
        language_and_word_map, language_and_prefix_map = self.get_language_specific_maps()
        language_and_request_type_to_words_map = {
            language: LanguageParser._get_flipped_dict(language_and_word_map[language])
                for language in language_and_word_map.keys()
        }
        language_and_request_type_to_prefix_map = {
            language: LanguageParser._get_flipped_dict(language_and_prefix_map[language])
                for language in language_and_word_map.keys()
        }
        return language_and_request_type_to_words_map, language_and_request_type_to_prefix_map

    def get_language_specific_descriptions(self) -> dict[str, dict[RequestType, str]]:
        language_map = {}
        for language, language_data in self.language_config.items():
            specific_language_request_to_description_map = {}
            for type_name, description in language_data.get("descriptions", {}).items():
                specific_language_request_to_description_map[RequestType[type_name]] = description
            language_map[language] = specific_language_request_to_description_map
        return language_map

    def get_word_to_language_map(self):
        word_to_language_map = {}
        for language, language_data in self.language_config.items():
            for word in language_data.get("words", {}).keys():
                word_to_language_map[word] = language
        return word_to_language_map

    @staticmethod
    def _get_flipped_dict(dct: dict) -> dict:
        flipped_dict = {value: [] for value in dct.values()}
        for key, value in dct.items():
            flipped_dict[value].append(key)
        return flipped_dict

LANGUAGES_CONFIG_PATH = Path(__file__).resolve().parent / "languages_config.yaml"
language_parser = LanguageParser(LANGUAGES_CONFIG_PATH)
LANG_WORD_TO_REQUEST_TYPE, LANG_PREFIX_TO_REQUEST_TYPE = language_parser.get_language_specific_maps()
FLAT_WORD_TO_REQUEST_TYPE, FLAT_PREFIX_TO_REQUEST_TYPE = language_parser.get_flattened_commands_map()
REQUEST_TYPE_TO_DESCRIPTION = language_parser.get_language_specific_descriptions()
REQUEST_TYPE_TO_WORDS, REQUEST_TYPE_TO_PREFIXES = language_parser.get_language_specific_request_type_to_words_prefixes_maps()
WORD_TO_LANGUAGE = language_parser.get_word_to_language_map()