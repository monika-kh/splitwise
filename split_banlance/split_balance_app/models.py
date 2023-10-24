from django.db import models
from django.db.models import JSONField


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.email


class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ("EQUAL", "Equal"),
        ("EXACT", "Exact"),
        ("PERCENT", "Percent"),
    ]

    paid_by = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name="paid_by")
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(max_length=10,
                                    choices=EXPENSE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    shares = JSONField(blank=True, null=True)
    owed_to_user = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.description


class ExpenseShare(models.Model):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="expense"
    )
    payer = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="payer")
    owed_to = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                related_name="owed_to")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.payer} owes {self.amount} to {self.owed_to}"


class SimplfyAmount(models.Model):
    payer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payer_on_behalf"
    )
    on_behalf_of = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="on_behalf_of"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
