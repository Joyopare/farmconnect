"""
URL configuration for farmconnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings

from django.urls import path
from farmers import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('farmers/', views.farmer_list, name='farmer_list'),
    path('register/', views.register, name='register'),
    path('farmers/', views.farmer_list, name='farmer_list'),
    path('search/', views.farmer_search, name='farmer_search'),
    path('track-order/', views.track_order, name='track_order'),
    path('create-checkout-session/<int:order_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<int:product_id>/update/', views.update_product, name='update_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('farmer/<str:username>/products/', views.farmer_products, name='farmer_products'),
    path('farmer/<str:username>/', views.farmer_profile, name='farmer_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
