from django.contrib import admin
from django.urls import path, include  
from django.conf import settings
from django.conf.urls.static import static
from petpals import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),  
    path('accounts/', include('registration.backends.simple.urls')),
    path('petpals/', include(('petpals.urls', 'petpals'), namespace='petpals')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
