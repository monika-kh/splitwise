from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models

from .constant import EXPENSE_TYPE_CHOICES


class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} - {self.email}"


class Expense(models.Model):
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paid_by")
    description = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MaxValueValidator(limit_value=10000000)],
    )
    expense_type = models.CharField(max_length=10, choices=EXPENSE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description


class ExpenseShare(models.Model):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="expense_shares"
    )
    owed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owed_to")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MaxValueValidator(limit_value=10000000)],
    )

    def __str__(self):
        return f"{self.expense.paid_by.name} owes {self.amount} to {self.owed_to}"
