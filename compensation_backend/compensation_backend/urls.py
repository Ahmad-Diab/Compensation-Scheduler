"""compensation_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import include, path
from rest_framework import routers
from compensationapp import views
# from rest_framework.authtoken.views import obtain_auth_token  # <-- Here

# router = routers.DefaultRouter()
# router.register(r'mainapp', views)

urlpatterns = [
    # path('', include(router.urls)),

    path('logout/', views.Logout.as_view(), name='Logout'),
    path('login/', views.Login.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('gucadmin/holidays/', views.Holidays.as_view(), name='Holidays'),
    path('gucadmin/compensations/', views.CompensationsView.as_view(), name='Compensations'),
    path('gucstaff/compensations/', views.StaffCompensations.as_view(), name='StaffCompensations'),
    path('gucstaff/preferences/', views.StaffPreferences.as_view(), name='StaffPreferences'),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # <-- And here
]

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)