
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

APP_NAME = settings.APP_NAME

urlpatterns = [
    path('', include('trustpay_landing.urls', namespace='landing')),
    path('', include('trustpay_auth.urls', namespace='auth')),
    path(f"{APP_NAME}-admin/", admin.site.urls),
    path('auth/', include('trustpay_user.urls', namespace='user')),
    path('auth/', include('trustpay_trx.urls', namespace='trx')),
    path('auth/', include('trustpay_admin.urls', namespace='adm')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = f"{APP_NAME}"
admin.site.site_title = f"{APP_NAME}"
admin.site.index_title = f"Welcome to {APP_NAME}"
