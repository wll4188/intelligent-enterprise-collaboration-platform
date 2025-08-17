from django.contrib import admin
from django.urls import path, re_path, include
from django.http import JsonResponse
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny


def healthz(request):
    return JsonResponse({"status": "ok"})

schema_view = get_schema_view(
    openapi.Info(
        title="Collab Platform API",
        default_version="v1",
        description="智能企业协作平台 API 文档",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz),
    # 兼容前端代理/历史调用：提供 /api/healthz/ 别名，返回相同结果
    path("api/healthz/", healthz),
    path("api/auth/", include("users.urls")),
    path("api/chat/", include("chat.urls")),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]