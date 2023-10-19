from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Expense)
admin.site.register(Room)

admin.site.register(UserRoom)
admin.site.register(ExpenseSplit)
admin.site.register(Owes)


