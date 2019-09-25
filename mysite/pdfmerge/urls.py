from django.urls import path

from . import views

urlpatterns = [
    path('merge',views.merge_pdf, name='merge_pdf'),
    path('purge',views.purge_pdf, name='purge_pdf'),
]