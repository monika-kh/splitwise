from django.urls import path

from .views import CreateExpensesView, ExpenseSplitView, UserList

urlpatterns = [
    path("users/", UserList.as_view(), name="user-list"),
    path("expenses/", CreateExpensesView.as_view(), name="expense-list"),
    path(
        "get-expences-split-list/<int:user_id>",
        ExpenseSplitView.as_view(),
        name="expense-share-list",
    ),
    path(
        "get-simplify_balance/<int:user_id>",
        ExpenseSplitView.as_view(),
        name="expense-share-list",
    ),
]
