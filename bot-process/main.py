from fastapi import FastAPI, Request
from RequestTypes import RequestType

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "I'm alive!"}

def get_request_type_payload_and_handler_from_text(text: str):
    text = text.strip().lower()
    if not text:
        return RequestType.INVALID, None, handle_invalid_request
    split_text = text.split()

    if text.startswith(RequestType.SEND_TO_LLM.value):
        return RequestType.SEND_TO_LLM, text[1:], send_to_llm
    if split_text[0] in RequestType:
        request_type = RequestType(split_text[0])
        payload = split_text[1:] if request_type != RequestType.GET_LIST else None
        if request_type == RequestType.ADD:
            handler = add_to_list
        elif request_type == RequestType.REMOVE:
            handler = remove_from_list
        elif request_type == RequestType.GET_LIST:
            handler = get_list
        else:
            handler = handle_invalid_request
        return request_type, payload, handler

    return RequestType.INVALID, None, handle_invalid_request

def send_to_llm(payload: str):
    # TODO: Implement
    pass

def add_to_list(payload: list[str]):
    # TODO: Implement when DB is setup
    pass

def remove_from_list(payload: list[str]):
    # TODO: Implement when DB is setup
    pass

def get_list(payload) -> list[str]:
    # TODO: Implement when DB is setup
    pass

def handle_invalid_request(payload):
    # TODO: Choose what to do here
    pass

@app.post("/webhook")
async def webhook(request: Request):
    req_json = await request.json()
    message_text = req_json["message"]["text"]

    request_type, payload, handler = get_request_type_payload_and_handler_from_text(message_text)
    handler(payload)

    return {"ok": True}