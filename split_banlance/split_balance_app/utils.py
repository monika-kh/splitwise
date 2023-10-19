from django.conf import settings
from django.core.mail import send_mail


def send_expense_notification_email(expense, user):
    subject = "You've been added to an expense"
    message = {"expense": expense, "user": user}
    plain_message = message
    from_email = settings.SENDER_MAIL
    recipient_list = [user.email]

    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=message
    )
