from django.core.management.base import BaseCommand
from faker import Faker
from fire.models import Locations, Incident, FireStation, FireTruck, Firefighters, WeatherConditions
from decimal import Decimal
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create initial data for the fire management application'

    def handle(self, *args, **kwargs):
        self.create_locations(10)
        self.create_fire_stations(5)
        self.create_firefighters(20)
        self.create_fire_trucks(10)
        self.create_incidents(10)
        self.create_weather_conditions(10)

    def create_locations(self, count):
        fake = Faker('en_PH')

        lat_range = (4.215806, 21.321780)
        lon_range = (116.438000, 126.597000)

        def random_latlon():
            return (
                Decimal(random.uniform(*lat_range)).quantize(Decimal('0.000001')),
                Decimal(random.uniform(*lon_range)).quantize(Decimal('0.000001'))
            )

        for _ in range(count):
            latitude, longitude = random_latlon()
            Locations.objects.create(
                name=fake.city(),
                latitude=latitude,
                longitude=longitude,
                address=fake.address(),
                city=fake.city(),
                country='Philippines'
            )
        self.stdout.write(self.style.SUCCESS('Initial data for locations created successfully.'))

    def create_fire_stations(self, count):
        fake = Faker('en_PH')

        lat_range = (4.215806, 21.321780)
        lon_range = (116.438000, 126.597000)

        def random_latlon():
            return (
                Decimal(random.uniform(*lat_range)).quantize(Decimal('0.000001')),
                Decimal(random.uniform(*lon_range)).quantize(Decimal('0.000001'))
            )

        for _ in range(count):
            latitude, longitude = random_latlon()
            FireStation.objects.create(
                name=fake.company(),
                latitude=latitude,
                longitude=longitude,
                address=fake.address(),
                city=fake.city(),
                country='Philippines'
            )
        self.stdout.write(self.style.SUCCESS('Initial data for fire stations created successfully.'))

    def create_firefighters(self, count):
        fake = Faker('en_PH')

        fire_stations = FireStation.objects.all()
        for _ in range(count):
            station = random.choice(fire_stations)
            Firefighters.objects.create(
                name=fake.name(),
                rank=fake.job(),
                experience_level=random.choice([choice[0] for choice in Firefighters.XP_CHOICES]),
                station=station
            )
        self.stdout.write(self.style.SUCCESS('Initial data for firefighters created successfully.'))

    def create_fire_trucks(self, count):
        fake = Faker()

        fire_stations = FireStation.objects.all()
        for _ in range(count):
            station = random.choice(fire_stations)
            FireTruck.objects.create(
                truck_number=fake.license_plate(),
                model=fake.word(),
                capacity=f'{random.randint(1000, 5000)} liters',
                station=station
            )
        self.stdout.write(self.style.SUCCESS('Initial data for fire trucks created successfully.'))

    def create_incidents(self, count):
        fake = Faker()

        locations = Locations.objects.all()
        for _ in range(count):
            location = random.choice(locations)
            Incident.objects.create(
                location=location,
                date_time=fake.date_time_this_year(before_now=True, after_now=False, tzinfo=timezone.get_current_timezone()),
                severity_level=random.choice([choice[0] for choice in Incident.SEVERITY_CHOICES]),
                description=fake.sentence()
            )
        self.stdout.write(self.style.SUCCESS('Initial data for incidents created successfully.'))

    def create_weather_conditions(self, count):
        fake = Faker()

        incidents = Incident.objects.all()
        for _ in range(count):
            incident = random.choice(incidents)
            WeatherConditions.objects.create(
                incident=incident,
                temperature=Decimal(random.uniform(20, 40)).quantize(Decimal('0.00')),
                humidity=Decimal(random.uniform(40, 100)).quantize(Decimal('0.00')),
                wind_speed=Decimal(random.uniform(0, 30)).quantize(Decimal('0.00')),
                weather_description=fake.sentence(nb_words=6)
            )
        self.stdout.write(self.style.SUCCESS('Initial data for weather conditions created successfully.'))