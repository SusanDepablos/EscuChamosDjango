from django.http import StreamingHttpResponse
import asyncio
from .models import Notification

clients = {}

class LiveNotification:
    @staticmethod
    async def stream(req, user_id):
        if user_id not in clients:
            clients[user_id] = []

        clients[user_id].append(req)

        count = await LiveNotification.get_count(user_id)
        yield f"data: {{ 'notifications': {count} }}\n\n"

        try:
            while True:
                new_count = await LiveNotification.get_count(user_id)
                if new_count != count:
                    count = new_count
                    yield f"data: {{ 'notifications': {count} }}\n\n"
                await asyncio.sleep(1)  # Usar asyncio.sleep para evitar bloqueo
        finally:
            clients[user_id].remove(req)

    @staticmethod
    async def get_count(user_id):
        return await Notification.objects.filter(receiver_user_id=user_id, is_seen=False).acount()

    @staticmethod
    def sse_endpoint(req, user_id):
        return StreamingHttpResponse(LiveNotification.stream(req, user_id), content_type='text/event-stream')
