from celery import shared_task
from .models import Comment, Post
from .utils import generate_auto_reply
import time

@shared_task
def send_auto_reply(comment_id, post_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        post = Post.objects.get(id=post_id)

        # Генерируем релевантный ответ с помощью AI
        reply_content = generate_auto_reply(post.content, comment.content)
        
        # Сохраняем ответ в комментарии
        comment.reply = reply_content
        comment.save()

    except Comment.DoesNotExist:
        print(f"Comment with id {comment_id} does not exist.")
    except Post.DoesNotExist:
        print(f"Post with id {post_id} does not exist.")