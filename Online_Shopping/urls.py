"""Online_Shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from view import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('myadmin/', myadmin, name='myadmin'),
    path('adminhome/',adminhome,name='adminhome'),
    path('addcategory/', addcategory, name='addcategory'),
    path('viewcategory/', viewcategory, name='viewcategory'),
    path('deletecategory/<int:id>', deletecategory, name='deletecategory'),
    path('updatecategory/<int:id>', updatecategory, name='updatecategory'),
    path('addproduct/', addproduct, name='addproduct'),
    path('viewproduct/', viewproduct, name='viewproduct'),
    path('deleteproduct/<int:id>', deleteproduct, name='deleteproduct'),
    path('updateproduct/<int:id>', updateproduct, name='updateproduct'),
    path('logout/',logout,name='logout'),
    path('users/',users,name='users'),
    path('deleteuser/<str:email>',deleteuser,name='deleteuser'),
    # client urls
    path('',home, name='home'),
    path('account/',account,name='account'),
    path('register/',register,name='register'),
    path('checkout/',checkout,name='checkout'),
    path('contact/',contact,name='contact'),
    path('userlogout/',userlogout,name='userlogout'),
    path('products/<int:id>',products,name='products'),
    path('single/<int:id>',single,name='single'),
    path('categorynames',categorynames,name='categorynames'),
    path('add_to_cart/<int:id>',add_to_cart,name='add_to_cart'),
    path('empty_cart',empty_cart,name='empty_cart'),
    path('inc_dec/<int:id>/<str:operation>',inc_dec,name='inc_dev'),
    path('proceed_to_pay',proceed_to_pay,name='proceed_to_pay'),
    path('payment_action',payment_action,name='payment_action'),
    path('thankspage',thankspage),
    # end of client urls
    path('TnC',TnC,name='TnC'),
    path('privacy',privacy,name='privacy')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
