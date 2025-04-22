
from django.contrib import admin
from django.urls import include,path
from Temp import views


urlpatterns = [
    path("Temp/", include("Temp.urls")),
    path("", include("Temp.urls")),
    path('submit_postcode/', views.submit_postcode, name='submit_postcode'),
    path('admin/', admin.site.urls),
    ]
