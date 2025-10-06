from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name='login'),
    # path('', views.home, name='home'),
    path('base/', views.base, name='base'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('feedback/', views.feedback, name='feedback'),
     path("satellites/", views.satellite_dashboard, name="satellite_dashboard"),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('analyst_dashboard/', views.analyst_dashboard, name='analyst_dashboard'),

    path("datasets", views.dataset_list, name="dataset_list"),
    path("create/", views.dataset_create, name="dataset_create"),
    path("<str:pk>/", views.dataset_detail, name="dataset_detail"),
    path("<str:pk>/edit/", views.dataset_update, name="dataset_update"),
    path("<str:pk>/delete/", views.dataset_delete, name="dataset_delete"),
]

# ✅ Static files serve karo sirf DEBUG mode mai
if settings.DEBUG:
    urlpatterns += static('/datasets/', document_root=settings.DATASETS_ROOT)
