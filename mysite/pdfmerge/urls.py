from django.urls import path

from . import views

urlpatterns = [
    path('pdf',views.merge_pdf, name='merge_pdf')
]