import calendar
import openpyxl
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, F, Case, When, DecimalField
from rest_framework.permissions import IsAuthenticated
from users.models import Client, User
from .models import Transaction, Invoice
from .serializers import TransactionSerializer, InvoiceSerializer
from datetime import timedelta
from django.utils import timezone


class TransactionListCreateAPIView(APIView):
    def get(self, request):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        transactions = Transaction.objects.filter(
            transaction_date__date__range=[start_of_week, end_of_week]
        ).order_by("-transaction_date")
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return None

    def get(self, request, pk):
        transaction = self.get_object(pk)
        if transaction is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    def put(self, request, pk):
        transaction = self.get_object(pk)
        if transaction is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        transaction = self.get_object(pk)
        if transaction is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvoiceListCreateAPIView(APIView):
    def get(self, request):
        invoices = Invoice.objects.select_related(
            "merchant", "client"
        ).prefetch_related("transactions")
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InvoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist:
            return None

    def get(self, request, pk):
        invoice = self.get_object(pk)
        if invoice is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)

    def put(self, request, pk):
        invoice = self.get_object(pk)
        if invoice is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = InvoiceSerializer(invoice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        invoice = self.get_object(pk)
        if invoice is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DailyAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        daily_transactions = Transaction.objects.filter(transaction_date__date=today)
        total_transactions = daily_transactions.count()

        new_users = User.objects.filter(date_joined__date=today).count()
        new_clients = Client.objects.filter(date_joined__date=today).count()

        all_users = User.objects.count()
        all_clients = Client.objects.count()

        users_percentage = (
            round((new_users / all_users) * 100, 2) if all_users > 0 else 0
        )
        clients_percentage = (
            round((new_clients / all_clients) * 100, 2) if all_clients > 0 else 0
        )

        total_amount_made = round(
            daily_transactions.aggregate(
                total=Sum("amount", output_field=DecimalField())
            )["total"]
            or 0,
            2,
        )

        total_profit = daily_transactions.aggregate(
            profit=Sum(
                Case(
                    When(amount__gt=0, then=F("amount")),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            loss=Sum(
                Case(
                    When(amount__lt=0, then=F("amount")),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
        )

        profit = round(total_profit["profit"] or 0, 2)
        loss = round(total_profit["loss"] or 0, 2)

        profit_loss = round(profit - abs(loss), 2)

        # Calculate yesterday's transactions
        yesterday_transactions = Transaction.objects.filter(
            transaction_date__date=yesterday
        )
        total_transactions_yesterday = yesterday_transactions.count()

        # Calculate the percentage change in total transactions
        if total_transactions_yesterday == 0:
            transactions_percentage = round(100 if total_transactions > 0 else 0, 2)
        else:
            transactions_percentage = round(
                (
                    (total_transactions - total_transactions_yesterday)
                    / total_transactions_yesterday
                )
                * 100,
                2,
            )

        # Calculate the total amount made yesterday
        total_amount_made_yesterday = round(
            yesterday_transactions.aggregate(
                total=Sum("amount", output_field=DecimalField())
            )["total"]
            or 0,
            2,
        )

        # Calculate the percentage change in total amount made
        if total_amount_made_yesterday == 0:
            amount_percentage_change = round(100 if total_amount_made > 0 else 0, 2)
        else:
            amount_percentage_change = round(
                (
                    (total_amount_made - total_amount_made_yesterday)
                    / total_amount_made_yesterday
                )
                * 100,
                2,
            )

        data = {
            "date": today,
            "total_transactions": total_transactions,
            "total_transactions_percentage": transactions_percentage,
            "new_users": new_users,
            "total_amount_made": total_amount_made,
            "total_amount_made_percentage": amount_percentage_change,
            "profit_loss": profit_loss,
            "new_clients": new_clients,
            "users_percentage": users_percentage,
            "clients_percentage": clients_percentage,
        }

        return Response(data)


class WeeklyActiveUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week -= timedelta(days=1)

        dates = [start_of_week + timedelta(days=i) for i in range(7)]

        active_users_counts = [
            User.objects.filter(date_joined__date=date).count() for date in dates
        ]

        days_of_week = list(calendar.day_abbr)
        data = [
            {"day": day, "date": date.strftime("%d %b, %Y"), "users": count}
            for day, date, count in zip(days_of_week, dates, active_users_counts)
        ]

        return Response(data)


class MonthlyTrafficSalesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        year_start = today.replace(month=1, day=1)
        months = [calendar.month_abbr[i] for i in range(1, 13)]

        monthly_data = []

        for month in range(1, 13):
            start_date = year_start.replace(month=month)
            end_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1)

            transactions = Transaction.objects.filter(
                transaction_date__date__gte=start_date,
                transaction_date__date__lt=end_date,
            )

            sales = (
                transactions.aggregate(total_sales=Sum("amount"))["total_sales"] or 0
            )
            traffic = transactions.count()

            monthly_data.append(
                {
                    "month": months[month - 1],
                    "traffic": traffic,
                    "sales": sales,
                }
            )

        return Response(monthly_data)


class ExportInvoicesToExcel(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        invoice_ids = request.data.get('invoice_ids', [])
        if not invoice_ids:
            return JsonResponse({'error': 'No invoice IDs provided.'}, status=400)

        invoices = Invoice.objects.filter(id__in=invoice_ids)
        if not invoices.exists():
            return JsonResponse({'error': 'No matching invoices found.'}, status=404)

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Invoices"

        headers = [
            "Client",
            "Merchant",
            "Issue Date",
            "Due Date",
            "Total Amount",
            "Status",
        ]
        sheet.append(headers)

        for invoice in invoices:
            sheet.append(
                [
                    str(invoice.client),
                    str(invoice.merchant),
                    invoice.issue_date.strftime("%Y-%m-%d %H:%M:%S"),
                    invoice.due_date.strftime("%Y-%m-%d %H:%M:%S"),
                    str(invoice.total_amount),
                    invoice.get_status_display(),
                ]
            )

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=invoices.xlsx"

        workbook.save(response)

        return response
