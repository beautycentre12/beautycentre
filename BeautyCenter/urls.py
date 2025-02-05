from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('bcentre/admin/', admin.site.urls),
    path('admin_tools_stats/', include('admin_tools_stats.urls')),
    path('', include('beautycenterapp.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('select2/', include('django_select2.urls')),  # Include this
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)    
