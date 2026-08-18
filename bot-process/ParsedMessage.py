from RequestTypes import RequestType

class ParsedMessage:
    def __init__(self, message: str, word_to_request_type: dict[str, RequestType], prefix_to_request_type: dict[str, RequestType]):
        self.text = message.lower().strip()
        self.lines = self.text.split("\n")
        self.first_line_words = self.lines[0].split()
        self.command_candidate = self.first_line_words[0] if self.first_line_words else None
        self._has_valid_command_or_prefix = (self.command_candidate in word_to_request_type.keys()
                                             or any(self.text.startswith(prefix) for prefix in prefix_to_request_type.keys()))
        self.first_line_item = " ".join(self.first_line_words[1:])

    def get_item_list(self) -> list[str]:
        if self._has_valid_command_or_prefix:
            return (([self.first_line_item] if self.first_line_item else [])
                            + [line.strip() for line in self.lines[1:] if line.strip()])
        return [line.strip() for line in self.lines if line.strip()]

    def get_prefixless_message(self):
        if not self.text:
            return ""
        return self.text[1:].strip()