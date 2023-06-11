from django.urls import path,re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.store,name='store'),
    path('<slug:slug>/',views.store,name='products_by_category'),
    path('<slug:slug>/<slug:product_slug>/',views.product_detail,name='product_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
