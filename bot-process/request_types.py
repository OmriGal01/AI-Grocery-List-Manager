from enum import Enum, auto

class RequestType(Enum):
    INVALID = auto()
    HELP = auto()
    ADD = auto()
    REMOVE = auto()
    CLEAR = auto()
    GET_LIST = auto()
    SEND_TO_LLM = auto()