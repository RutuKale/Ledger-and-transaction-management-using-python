from rest_framework import viewsets
from .models import Ledger, Transaction
from .serializers import LedgerSerializer, TransactionSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.dateparse import parse_date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import io

def home(request):
    return HttpResponse("Welcome to the Ledger Management System!")

class LedgerViewSet(viewsets.ModelViewSet):
    queryset = Ledger.objects.all()
    serializer_class = LedgerSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=True, methods=['get'])
    def filter_by_date(self, request, pk=None):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        ledger = self.get_object()
        transactions = Transaction.objects.filter(
            ledger=ledger,
            date__range=[parse_date(start_date), parse_date(end_date)]
        )
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        ledger = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        transactions = Transaction.objects.filter(
            ledger=ledger,
            date__range=[parse_date(start_date), parse_date(end_date)]
        )

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        textobject = p.beginText(40, 750)
        textobject.setFont("Helvetica", 12)
        textobject.textLines(f"Transactions for {ledger.name}")

        for txn in transactions:
            textobject.textLine(f"{txn.date} | {txn.amount} | {txn.type}")

        p.drawText(textobject)
        p.showPage()
        p.save()

        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

def generate_pdf(request, ledger_id):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return HttpResponse("Missing start_date or end_date parameters", status=400)

    try:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
    except ValueError as e:
        return HttpResponse(f"Date parsing error: {e}", status=400)

    if not start_date or not end_date:
        return HttpResponse("Invalid date format. Use YYYY-MM-DD.", status=400)

    transactions = Transaction.objects.filter(
        ledger_id=ledger_id,
        date__range=[start_date, end_date]
    )

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Transactions Report")
    y = 730
    for transaction in transactions:
        p.drawString(100, y, f"Transaction ID: {transaction.id}, Amount: {transaction.amount}, Date: {transaction.date}")
        y -= 20
    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')