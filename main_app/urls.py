from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),  # Main page
    path('profile/', views.volunteer_profile, name="volunteer_profile"),  # Volunteer's working profile
    path('order-done/<int:order_id>', views.order_done, name="order_done"),  # Internal API to close orders implicitly
]
