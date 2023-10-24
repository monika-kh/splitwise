from collections import defaultdict

from django.conf import settings

from .models import ExpenseShare, User
from .tasks import send_email_task


def send_mail(expense, shares):
    send_email_task(
        subject=f"Amount to pay for the expense- {shares.expense.description} on date: {shares.expense.created_at.date()}",
        message=f"You have to pay amount {shares.amount} for the expense {shares.expense.description}paid by {shares.payer.name}.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[shares.owed_to.email],
    )


def split_expense(expense):
    """
    Function to check the expense_type and split the amoutn between the users.
    """
    if expense.expense_type == "PERCENT":
        # Handle expenses of type 'PERCENT'
        total_percent = sum(expense.shares.values())
        if total_percent == 100:
            total_amount = expense.amount
            amount_per_percent = total_amount / 100
            for user_id, percent in expense.shares.items():
                if user_id != expense.paid_by:
                    ower = User.objects.get(id=user_id)
                    user = expense.paid_by
                    owed_to_user = ower
                    owed_amount = amount_per_percent * percent
                    shares = ExpenseShare.objects.create(
                        expense=expense,
                        payer=user,
                        owed_to=owed_to_user,
                        amount=owed_amount,
                    )
                    send_mail(expense, shares)
                else:
                    pass
        else:
            expense.delete()
            return False

    elif expense.expense_type == "EXACT":
        # Handle expenses of type 'EXACT'
        exact_amount_per_person = expense.amount
        for user in expense.owed_to_user.all():
            if user != expense.paid_by:
                shares = ExpenseShare.objects.create(
                    expense=expense,
                    payer=expense.paid_by,
                    owed_to=user,
                    amount=exact_amount_per_person,
                )
                send_mail(expense, shares)
            else:
                pass
    elif expense.expense_type == "EQUAL":
        # Handle expenses of type 'EQUAL'
        total_amount = expense.amount
        owes_to_users = expense.owed_to_user.all()
        amount_per_person = total_amount / len(owes_to_users)
        for user in owes_to_users:
            if user != expense.paid_by:
                shares = ExpenseShare.objects.create(
                    expense=expense,
                    payer=expense.paid_by,
                    owed_to=user,
                    amount=amount_per_person,
                )
                send_mail(expense, shares)
            else:
                pass


def get_balance(total_amount_to_pay, total_amount_to_receive):
    """
    Function to get the details of the amount to pay to someone and to get from somone.
    """
    user_balances = {}

    for item in total_amount_to_pay:
        user = item["payer__name"]
        amount_to_pay = item["amount_to_pay"]
        if user in user_balances:
            user_balances[user] -= amount_to_pay
        else:
            user_balances[user] = -amount_to_pay

    for item in total_amount_to_receive:
        user = item["owed_to__name"]
        amount_to_pay = item["amount_to_pay"]
        if user in user_balances:
            user_balances[user] += amount_to_pay
        else:
            user_balances[user] = amount_to_pay

    user_balances = {
        user: balance for user, balance in user_balances.items() if balance != 0
    }

    users_to_pay = [
        {"payer__name": user, "amount_to_pay": abs(amount)}
        for user, amount in user_balances.items()
        if amount < 0
    ]
    users_to_receive = [
        {"owed_to__name": user, "amount_to_receive": amount}
        for user, amount in user_balances.items()
        if amount > 0
    ]
    sum_total_pay = sum(item["amount_to_pay"] for item in users_to_pay)

    sum_total_receive = sum(item["amount_to_receive"] for item in users_to_receive)

    return {
        "total_amount_to_pay": users_to_pay,
        "total_amount_receive_from": users_to_receive,
        "sum_total_pay": sum_total_pay,
        "sum_total_receive": sum_total_receive,
    }


def simplify_balances(user_amount_to_pay, user_amount_to_receive):
    balances_to_pay = defaultdict(int)
    balances_to_receive = defaultdict(int)

    for item in user_amount_to_pay:
        payer = item["payer__name"]
        amount_to_pay = item["amount_to_pay"]
        balances_to_pay[payer] -= amount_to_pay

    for item in user_amount_to_receive:
        owed_to = item["owed_to__name"]
        amount_to_receive = item["amount_to_pay"]
        balances_to_receive[owed_to] += amount_to_receive

    # Simplify balances
    for payer, amount_to_pay in balances_to_pay.items():
        for owed_to, amount_to_receive in balances_to_receive.items():
            settle_amount = min(amount_to_pay, amount_to_receive)
            if settle_amount > 0:
                balances_to_pay[payer] -= settle_amount
                balances_to_receive[owed_to] -= settle_amount

                transaction = {
                    "payer__name": owed_to,
                    "amount_to_pay": settle_amount,
                    "owed_to__name": payer,
                }
                user_amount_to_pay.append(transaction)

    user_amount_to_pay = [
        item for item in user_amount_to_pay if item["amount_to_pay"] != 0
    ]
    return user_amount_to_pay
