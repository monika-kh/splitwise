from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail

logger = get_task_logger(__name__)


@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    """
    Task to send an email using Django's send_mail function.
    """
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)


@shared_task
def send_weekly_reminder_email():
    from django.db.models import Sum

    from .models import ExpenseShare, User

    logger.info("start task")
    users = User.objects.all()
    for user in users:
        total_amount_to_pay = (
            ExpenseShare.objects.filter(owed_to=4)
            .values("payer__name")
            .annotate(amount_to_pay=Sum("amount"))
        )
        expenses_owe = sum(item["amount_to_pay"] for item in total_amount_to_pay)
        total_amount_to_receive = (
            ExpenseShare.objects.filter(payer=user)
            .values("owed_to__name")
            .annotate(amount_to_pay=Sum("amount"))
        )
        expenses_get = sum(item["amount_to_pay"] for item in total_amount_to_receive)

        subject = "Weekly Expense Reminder"
        message = f"Hello {user.name},\n\n"
        message += "Here are your weekly expense reminders:\n\n"

        if total_amount_to_pay:
            message += "Expenses you owe:\n"
            for expense in total_amount_to_pay:
                message += f"- {expense['amount_to_pay']} to {expense['payer__name']}\n"
                message += f"- Total amount to pay:- {expenses_owe} \n"

        if total_amount_to_receive:
            message += "Expenses you should get:\n"
            for expense in total_amount_to_receive:
                message += (
                    f"- {expense['amount_to_pay']} from {expense['owed_to__name']}\n"
                )
                message += f"- Total amount to receive:- {expenses_get} \n"

        message += "\nPlease settle these expenses as soon as possible."

        send_mail(
            subject,
            message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("end task")
