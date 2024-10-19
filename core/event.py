# from django.http import StreamingHttpResponse
# import time
# from .models import Notification

# clients = {}

# class LiveNotification:
#     @staticmethod
#     def stream(req, user_id):
#         if user_id not in clients:
#             clients[user_id] = []

#         clients[user_id].append(req)

#         def generate():
#             count = LiveNotification.get_count(user_id)
#             yield f"data: {{ 'notifications': {count} }}\n\n"

#             try:
#                 while True:
#                     new_count = LiveNotification.get_count(user_id)
#                     if new_count != count:
#                         count = new_count
#                         yield f"data: {{ 'notifications': {count} }}\n\n"

#                     time.sleep(1)
#             finally:
#                 clients[user_id].remove(req)

#         return generate()

#     @staticmethod
#     def get_count(user_id):
#         return Notification.objects.filter(receiver_user_id=user_id, is_read=False).count()

#     @staticmethod
#     def sse_endpoint(req, user_id):
#         return StreamingHttpResponse(LiveNotification.stream(req, user_id), content_type='text/event-stream')
