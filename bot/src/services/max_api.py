import httpx
from typing import Optional, Dict, Any, List
from config import settings


class MaxApiService:
    def __init__(self):
        self.base_url = settings.max_api_url
        self.token = settings.max_bot_token

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        params = kwargs.get('params', {})
        params['access_token'] = self.token

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def send_message(self, chat_id: int, text: str, attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        data = {
            "text": text,
            "attachments": attachments or [],
            "notify": True
        }

        return await self._make_request(
            "POST",
            "/messages",
            params={"chat_id": chat_id},
            json=data
        )

    async def send_message_with_keyboard(self, chat_id: int, text: str, buttons: List[List[Dict]]) -> Dict[str, Any]:
        attachments = [{
            "type": "inline_keyboard",
            "payload": {
                "buttons": buttons
            }
        }]

        return await self.send_message(chat_id, text, attachments)

    async def edit_message(self, message_id: str, new_message: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request(
            "PUT",
            "/messages",
            params={"message_id": message_id},
            json=new_message
        )

    async def answer_callback(self, callback_id: str, message: Optional[Dict] = None,
                              notification: Optional[str] = None) -> Dict[str, Any]:
        data = {}
        if message:
            data["message"] = message
        if notification:
            data["notification"] = notification

        return await self._make_request(
            "POST",
            "/answers",
            params={"callback_id": callback_id},
            json=data
        )

    async def get_chat_info(self, chat_id: int) -> Dict[str, Any]:
        return await self._make_request("GET", f"/chats/{chat_id}")

    async def set_webhook(self, url: str, secret: Optional[str] = None) -> Dict[str, Any]:
        data = {
            "url": url,
            "update_types": [
                "message_created",
                "message_callback",
                "bot_started",
                "bot_stopped"
            ]
        }

        if secret:
            data["secret"] = secret

        return await self._make_request("POST", "/subscriptions", json=data)

    async def delete_webhook(self, url: str) -> Dict[str, Any]:
        return await self._make_request("DELETE", "/subscriptions", params={"url": url})

    async def get_my_info(self) -> Dict[str, Any]:
        return await self._make_request("GET", "/me")