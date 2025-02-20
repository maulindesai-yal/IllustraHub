"""
URL configuration for illustrahub project.

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
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from authenticate.views import (
    register_view, 
    login_view, 
    logout_view,
    profile_view,
    home_view,
    forgot_password_view,
    reset_password_view
)
from mains.views import (
    collection_view,
    upload_illustration_view,
    illustrators_view,
    about_us_view,
    contact_us_view,
    illustrator_details_view,
    illustration_store_view,
    illustration_details_view,
    add_to_cart,view_cart,remove_from_cart,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('simple_user_profile/', profile_view, name='simple_user_profile'),
    path('illustrator_profile/', profile_view, name='illustrator_profile'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', reset_password_view, name='reset_password'),

    path('collection/',collection_view,name='collection'),
    path('upload illustration/',upload_illustration_view,name='upload_illustration'),
    path('illustrators',illustrators_view,name='illustrators'),
    path('about us/',about_us_view,name='about_us'),
    path('contact us/',contact_us_view,name='contact_us'),
    path('illustrator/<str:email>/',illustrator_details_view,name='illustrator_details'),
    path('illustration store/',illustration_store_view, name = 'illustration_store'),
    path('illustration_details/<str:email>/',illustration_details_view, name = 'illustration_details'),
    path('add-to-cart/<int:illustration_id>/', add_to_cart, name='add_to_cart'),
    path('your_cart/', view_cart, name='view_cart'),
    path('remove-from-cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#STATIC_URL,STATIC_ROOT