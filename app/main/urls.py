from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('buy/<int:item_id>/', views.get_session_id, name='get_session_id'),
    path('item/<int:item_id>/', views.get_item_page, name='get_item_page'),
    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),
    path('cart/', views.cart_view, name='cart'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
