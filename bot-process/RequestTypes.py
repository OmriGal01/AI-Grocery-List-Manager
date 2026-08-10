from enum import Enum

class RequestType(Enum):
    INVALID = "invalid"
    SEND_TO_LLM = "!"
    ADD = "add"
    REMOVE = "remove"
    GET_LIST = "list"