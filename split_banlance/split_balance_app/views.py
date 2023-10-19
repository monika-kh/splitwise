from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from split_balance_app.utils import send_expense_notification_email

from .models import Expense, ExpenseSplit, Owes, User
from .serializers import ExpenseSerializer, ExpenseSplitSerializer


class ExpenseList(APIView):
    """
    Get the list of the expenses.
    """

    def get(self, request):
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailView(APIView):
    """
    Get, update and delete particular expenses.
    """

    def get_object(self, pk):
        try:
            return Expense.objects.get(pk=pk)
        except Expense.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    def put(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = self.get_object(pk)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateExpenseSplit(APIView):
    """
    Split expense between user and send email.
    """

    def post(self, request):
        serializer = ExpenseSplitSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            exist_ExpenseSplit = ExpenseSplit.objects.filter(
                expense=data["expense"], user=data["user"]
            )
            if not exist_ExpenseSplit:
                if data["expense"].expense_type == "PERCENT":
                    total = data["expense"].amount
                    if total > 0:
                        ExpenseSplit.objects.create(
                            expense=data["expense"],
                            user=data["user"],
                            amount=(total / 100) * data["amount"],
                        )
                else:
                    serializer.save()

            else:
                expense_split = exist_ExpenseSplit.first()
                if data["expense"].expense_type == "PERCENT":
                    total = data["expense"].amount
                    if total > 0:
                        expense_split.amount = (total / 100) * data["amount"]
                        expense_split.save()
                else:
                    expense_split.amount = data["amount"]
                    expense_split.save()
            expenses = ExpenseSplit.objects.filter(
                expense=data["expense"]).users.all()
            users = User.objects.filter(user__in=expenses)
            for user in users:
                send_expense_notification_email(data["expense"], user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllUsersOwesView(APIView):
    """
    Get list of all users with the from whom amount has to collect.
    """

    def get(self, request):
        qs = Owes.objects.all()
        rel = []
        if qs:
            for x in qs:
                rel.append(x.__str__())
        return Response({"result": rel})


class SelfOwesView(APIView):
    """
    Get the amount with the user to whom particular user to pay.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        usr = self.get_object(pk)
        all_owes = usr.owes_to.all()
        rel = []
        if all_owes:
            for x in all_owes:
                rel.append(x.__str__())
        return Response({"result": rel})
