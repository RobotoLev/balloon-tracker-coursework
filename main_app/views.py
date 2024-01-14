from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Order

# Create your views here.


def order_done(request, order_id: int):
    """
    Handles the internal API (closes an order if no access violation)
    """
    if request.method == 'POST':
        volunteer = request.user
        order = Order.objects.get(id=order_id)
        if order.volunteer == volunteer:
            order.done = True
            order.save()
            return HttpResponse("ok")


def index(request):
    """
    Handles the main page
    """
    orders = Order.objects.all()
    orders_groups = dict()
    for order in orders:
        key = order.room + '|||' + order.place
        if key in orders_groups:
            if order.done:
                orders_groups[key][3].append(order.balloon_color)
            else:
                orders_groups[key][4].append(order.balloon_color)
        else:
            if order.done:
                orders_groups[key] = [order.room, order.place, order.author_name, [order.balloon_color], []]
            else:
                orders_groups[key] = [order.room, order.place, order.author_name, [], [order.balloon_color]]

    return render(request, 'index.html', context={
        "orders_groups": orders_groups.items()
    })


@login_required
def volunteer_profile(request):
    """
    Handles volunteer's working profile
    """
    volunteer = request.user

    return render(request, 'profile.html', context={
        "orders": Order.objects.filter(volunteer=volunteer).all()
    })
