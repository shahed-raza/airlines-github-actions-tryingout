from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect

from .models import Flight, Passenger

# Create your views here.
def index(request):
    return render(request, "flights/index.html", {
        "flights": Flight.objects.all()
    })


def flight(request, flight_id):
    try:
        flight = Flight.objects.get(pk=flight_id)
    except Flight.DoesNotExist:
        return HttpResponseNotFound(request)

    return render(request, "flights/flight.html", {
        "flight": flight,
        "passengers": flight.passengers.all(), # type: ignore
        "non_passengers": Passenger.objects.exclude(flights=flight).all()
    })


def book(request, flight_id):
    if request.method == "POST":
        try:
            flight = Flight.objects.get(pk=flight_id)
        except Flight.DoesNotExist:
            return HttpResponseNotFound(request)

        try:
            passenger = Passenger.objects.get(pk=int(request.POST["passenger_id"]))
        except Passenger.DoesNotExist:
            return HttpResponseNotFound(request)

        passenger.flights.add(flight)
        return redirect("flight", flight_id=flight.id) # type: ignore
