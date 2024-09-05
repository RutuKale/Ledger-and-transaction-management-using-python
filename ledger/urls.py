from django.urls import path
from .views import generate_pdf

urlpatterns = [
    path('transactions/<int:ledger_id>/generate_pdf/', generate_pdf, name='generate_pdf'),
]