from django.db import models


class CreateUpdate(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UserRoom(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.room.name


class Expense(CreateUpdate):
    EXPENSE_TYPE_CHOICES = (
        ("EQUAL", "Equal"),
        ("EXACT", "Exact"),
        ("PERCENT", "Percent"),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_type = models.CharField(
        max_length=10,
        choices=EXPENSE_TYPE_CHOICES
        )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.created_by.name


class ExpenseSplit(CreateUpdate):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="expense_splits"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_splits")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.user.name


class Owes(CreateUpdate):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    owes_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owes_to")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.name} owes {self.amount} to {self.owes_to.name} "
