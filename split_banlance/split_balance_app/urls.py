from django.urls import path

from .views import (
    ExpenseList,
    ExpenseDetailView,
    CreateExpenseSplit,
    SelfOwesView,
    AllUsersOwesView,
)

urlpatterns = [
    path("expenses/", ExpenseList.as_view(), name="expense_detail"),
    path("expenses/<int:pk>/", ExpenseDetailView.as_view(),
        name="expense_detail"
    ),
    path("expense-splits/", CreateExpenseSplit.as_view(),
        name="expense_split_list"
    ),
    path(
        "users-owes/<int:pk>/", SelfOwesView.as_view(),
        name="all_users_owes_lends_view"
    ),
    path("users-owes/", AllUsersOwesView.as_view(),
        name="all_users_owes_lends_view"
    ),
]
