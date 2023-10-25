from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Expense, ExpenseShare, User
from .serializers import ExpenseSerializer, UserSerializer
from .utils import get_balance, simplify_balances, split_expense


class UserList(APIView):
    def get(self, request):
        """
        Get list of users.
        """
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class CreateExpensesView(APIView):
    def get(self, request):
        """
        Get list of expenses created.
        """
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create expenses and split the shares of each participants.
        """
        expense_serializer = ExpenseSerializer(data=request.data)
        if expense_serializer.is_valid():
            expense = expense_serializer.save()
            split_balance = split_expense(expense, request.data)
            if split_balance is False:
                return Response(
                    {"message": "Sum of percentage/amount not accurate"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": "Expense added successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                expense_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class ExpenseSplitView(APIView):
    """
    Api to get total amount that had to pay to payer and total amount has to receive from the owes.
    """

    def get(self, request, user_id):
        total_amount_to_pay = (
            ExpenseShare.objects.filter(owed_to=user_id)
            .values("expense__paid_by__name")
            .annotate(amount_to_pay=Sum("amount"))
        )
        total_amount_to_receive = (
            ExpenseShare.objects.filter(expense__paid_by=user_id)
            .values("owed_to__name")
            .annotate(amount_to_pay=Sum("amount"))
        )

        balance_list = get_balance(total_amount_to_pay, total_amount_to_receive)

        if "get-simplify_balance" in request.path:
            simplified_balances = simplify_balances(
                total_amount_to_pay, total_amount_to_receive
            )
            return Response(simplified_balances, status=status.HTTP_200_OK)
        return Response(balance_list, status=status.HTTP_200_OK)
