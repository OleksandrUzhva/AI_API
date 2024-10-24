from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Count, Q
from django.utils.dateparse import parse_date
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from ninja import Router
from ninja import Schema
from ninja import Query
from ninja.security import HttpBearer
from ninja.errors import HttpError

from datetime import timedelta

from posts.models import Post, Comment
from .utils import check_toxicity
from .tasks import send_auto_reply


router = Router()

class RegisterSchema(Schema):
    username: str
    password: str

class LoginSchema(Schema):
    username: str
    password: str

class CreatePostSchema(Schema):
    title: str
    content: str

class CreateCommentSchema(Schema):
    content: str

class CommentsAnalyticsParams(Schema):
    date_from: str
    date_to: str

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            return user
        except Exception:
            return None 

# Регистрация пользователя
@router.post("/register/")
def register(request, payload: RegisterSchema):
    user = User.objects.create_user(username=payload.username, password=payload.password)
    return {"success": True, "user_id": user.id}

# Вход пользователя
@router.post("/login/")
def login(request, payload: LoginSchema):
    user = authenticate(username=payload.username, password=payload.password)
    if not user:
        raise HttpError(400, "Неправильные учетные данные")
    
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

# Управление постами
@router.post("/create/", auth=AuthBearer())
def create_post(request, payload: CreatePostSchema):
    user = request.auth
    
    is_blocked = check_toxicity(payload.content)
    
    post = Post.objects.create(
        title=payload.title, 
        content=payload.content, 
        user=user, 
        is_blocked=is_blocked  
    )
    
    if is_blocked:
        message = "Ваш пост заблокирован из-за нецензурной лексики."
    else:
        message = "Ваш пост успешно размещен."

    return {
        "post_id": post.id,
        "message": message  
    }

# Управление комментариями
@router.post("/{post_id}/comments/", auth=AuthBearer())
def create_comment(request, post_id: int, payload: CreateCommentSchema):
    user = request.auth
    
    is_blocked = check_toxicity(payload.content)

    post = Post.objects.get(id=post_id)
    comment = Comment.objects.create(
        post=post, 
        content=payload.content,
        user=user,
        is_blocked=is_blocked
    )

    # Если автоответ включен, запускаем задачу с задержкой
    if post.auto_reply_enabled and not is_blocked:
        delay_seconds = post.auto_reply_delay.total_seconds() if post.auto_reply_delay else 0
        send_auto_reply.apply_async((comment.id, post.id), countdown=delay_seconds)

    if is_blocked:
        message = "Ваш комментарий заблокирован из-за нецензурной лексики."
    else:
        message = "Ваш комментарий успешно размещен."

    return {"comment_id": comment.id, "message": message}

# @router.post("/{post_id}/comments/", auth=AuthBearer())
# def create_comment(request, post_id: int, payload: CreateCommentSchema):
#     user = request.auth
    
#     is_blocked = check_toxicity(payload.content)

#     post = Post.objects.get(id=post_id)
#     comment = Comment.objects.create(
#         post=post, 
#         content=payload.content,
#         user=user,
#         is_blocked=is_blocked
#     )

#     if is_blocked:
#         message = "Ваш коментарий заблокирован из-за нецензурной лексики."
#     else:
#         message = "Ваш коментарий успешно размещен."

#     return {"comment_id": comment.id,
#             "message": message  
#     }

# Аналитика коментариев 
@router.get("/comments-daily-breakdown/")
def comments_daily_breakdown(request, params: CommentsAnalyticsParams = Query(...)):
    date_from = parse_date(params.date_from)
    date_to = parse_date(params.date_to)

    if not date_from or not date_to:
        raise HttpError(400, "Неправильний формат дати")

    # Делаем запрос в базу данных для анализа 
    analytics = (
        Comment.objects.filter(created_at__date__range=(date_from, date_to))
        .values("created_at__date")
        .annotate(
            total_comments=Count("id"),  
            blocked_comments=Count("id", filter=Q(is_blocked=True))  
        )
        .order_by("created_at__date")  
    )

    result = []
    current_date = date_from

    while current_date <= date_to:
        day_data = next((entry for entry in analytics if entry['created_at__date'] == current_date), None)
        result.append({
            "date": current_date,
            "total_comments": day_data["total_comments"] if day_data else 0,
            "blocked_comments": day_data["blocked_comments"] if day_data else 0
        })
        current_date += timedelta(days=1)

    return result