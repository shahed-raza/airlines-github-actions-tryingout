from django.http import response
from django.test import TestCase, Client
from django.db.models import Max

from .models import Airport, Flight, Passenger

# Create your tests here.
class FlightTestCase(TestCase):

    # create dummy data THE set_up
    def setUp(self) -> None:
        # create airports
        a1 = Airport.objects.create(code="AAA", city="City A")
        a2 = Airport.objects.create(code="BBB", city="City B")

        # create flights
        f1 = Flight.objects.create(origin=a1, destination=a2, duration=100)
        f2 = Flight.objects.create(origin=a1, destination=a1, duration=200)
        f3 = Flight.objects.create(origin=a1, destination=a2, duration=-100)

        return super().setUp()

    # test departures count
    def test_departures_count(self) -> None:
        # test departures count of flight 'a1' should be 3
        a1 = Airport.objects.get(code="AAA")
        self.assertEqual(a1.departures.count(), 3) # type: ignore

    # test arrivals count
    def test_arrivals_count(self) -> None:
        # test arrivals of a1 should be 1
        a1 = Airport.objects.get(code="AAA")
        self.assertEqual(a1.arrivals.count(), 1) # type: ignore

    # test valid flight
    def test_valid_flight(self) -> None:
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")

        f1 = Flight.objects.get(origin=a1, destination=a2, duration=100)
        self.assertTrue(f1.is_valid_flight())

    # test invalid destination flight
    def test_invalid_flight_destination(self) -> None:
        # test flight f2 has invalid destination, since both origin & destination are same
        a1 = Airport.objects.get(code="AAA")

        f2 = Flight.objects.get(origin=a1, destination=a1, duration=200)
        self.assertFalse(f2.is_valid_flight())

    # test invalid duration flight
    def test_invalid_flight_duration(self) -> None:
        # flight f3 has invalid duration
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")

        f3 = Flight.objects.get(origin=a1, destination=a2, duration=-100)
        self.assertFalse(f3.is_valid_flight())


    # TESTING VIEWS

    # test index view
    def test_index(self):
        c = Client()
        response = c.get("/flights/")

        self.assertEqual(response.status_code, 200)

        # should get all the 3 created flights
        self.assertEqual(response.context["flights"].count(), 3)


    # test valid flight page
    def test_valid_flight_page(self):
        a1 = Airport.objects.get(code="AAA")
        f = Flight.objects.get(origin=a1, destination=a1, duration=200)

        c = Client()
        response = c.get(f"/flights/{f.id}") # type: ignore

        self.assertEqual(response.status_code, 200)

    # test invalid flight page
    def test_invalid_flight_page(self):
        max_id = Flight.objects.aggregate(Max("id"))["id__max"]

        c = Client()
        response = c.get(f"/flights/{max_id + 1}")

        self.assertEqual(response.status_code, 404)

    # test passenger count
    def test_flight_page_passengers(self):
        f = Flight.objects.get(pk=1)
        p = Passenger.objects.create(first="Alice", last="Adams")
        p.flights.add(f)

        c = Client()
        response = c.get(f"/flights/{f.id}") # type: ignore

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["passengers"].count(), 1)

    # test non-passengers count
    def test_flight_non_passengers(self):
        f = Flight.objects.get(pk=1)
        p = Passenger.objects.create(first="Alice", last="Adams")

        c = Client()
        response = c.get(f"/flights/{f.id}") # type: ignore

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["non_passengers"].count(), 1)
