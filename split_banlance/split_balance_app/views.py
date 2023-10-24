from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Expense, ExpenseShare, User
from .serializers import (ExpenseSerializer,
                          UserSerializer)
from .utils import get_balance, simplify_balances, split_expense


class UserList(APIView):
    def get(self, request):
        '''
        Get list of users.
        '''
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class CreateExpensesView(APIView):
    def get(self, request):
        '''
        Get list of expenses created.
        '''
        expenses = Expense.objects.all()
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    def post(self, request):
        '''
        Create expenses and split the shares of each participants.
        '''
        expense_serializer = ExpenseSerializer(data=request.data)
        if expense_serializer.is_valid():
            expense = expense_serializer.save()
            if ("owed_to_user" in request.data) and (
                request.data["owed_to_user"] is not []
            ):
                for user_id in request.data["owed_to_user"]:
                    user = User.objects.get(id=user_id)
                    expense.owed_to_user.add(user)

                split_balance = split_expense(expense)

            if ("shares" in request.data) and (
                request.data["shares"] is not None
            ):
                for user_id in request.data["shares"].keys():
                    user = User.objects.get(id=int(user_id))
                    expense.owed_to_user.add(user)
                split_balance = split_expense(expense)
            if split_balance is False:
                return Response(
                    {"message": "Percentage sum is not equal to 100"},
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
    '''
    Api to get total amount that had to pay to payer and total amount has to receive from the owes.
    '''

    def get(self, request, user_id):
        total_amount_to_pay = (
            ExpenseShare.objects.filter(owed_to=user_id)
            .values("payer__name")
            .annotate(amount_to_pay=Sum("amount"))
        )
        total_amount_to_receive = (
            ExpenseShare.objects.filter(payer=user_id)
            .values("owed_to__name")
            .annotate(amount_to_pay=Sum("amount"))
        )

        balance_list = get_balance(
            total_amount_to_pay, 
            total_amount_to_receive)

        if "get-simplify_balance" in request.path:
            simplified_balances = simplify_balances(
                total_amount_to_pay, total_amount_to_receive
            )
            return Response(simplified_balances, status=status.HTTP_200_OK)
        return Response(balance_list, status=status.HTTP_200_OK)
