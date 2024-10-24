from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from posts.api import router as posts_router

api = NinjaAPI()

api.add_router("/posts/", posts_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]