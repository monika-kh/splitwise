from .models import Expense, ExpenseSplit, Owes
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Expense)
def expense_post_save(sender, instance, created, **kwargs):
    if created:
        users_in_room = instance.room.userroom_set.all()
        if instance.expense_type == "EQUAL":
            if users_in_room:
                total_amount = instance.amount
                equal_amount = total_amount/users_in_room.count()
                users = users_in_room.exclude(user=instance.paid_by)
                if users:
                    for x in users:
                        ExpenseSplit.objects.create(
                            expense = instance,
                            user = x.user,
                            amount = equal_amount
                        )
        print(f"New expense '{instance.description}' has been saved!")
    else:
        print(f"Expense '{instance.description}' has been updated!")

@receiver(post_save, sender=ExpenseSplit)
def expense_post_save(sender, instance, created, **kwargs):
    if created:
        owes = Owes.objects.filter(user = instance.user, owes_to = instance.expense.paid_by,)
        if not owes:
            Owes.objects.create(
                user = instance.user,
                owes_to = instance.expense.paid_by,
                amount = instance.amount,
            )
        else:
            owes = owes.first() 
            owes.amount = float(owes.amount + instance.amount)
            owes.save()
    else:
        print(f"Expense '{instance.description}' has been updated!")

