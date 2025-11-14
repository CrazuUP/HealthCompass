from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class User(BaseModel):
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_bot: bool

class Recipient(BaseModel):
    chat_id: int
    chat_type: str
    user_id: Optional[int] = None

class MessageBody(BaseModel):
    mid: str
    seq: int
    text: Optional[str] = None
    attachments: Optional[List[Dict]] = None

class Message(BaseModel):
    sender: User
    recipient: Recipient
    timestamp: int
    body: MessageBody

class Callback(BaseModel):
    timestamp: int
    callback_id: str
    payload: str
    user: User

class Update(BaseModel):
    update_type: str
    timestamp: int
    message: Optional[Message] = None
    callback: Optional[Callback] = None
    chat_id: Optional[int] = None
    user: Optional[User] = None