import random
import string

from accounts.models import User


def generate_username(first_name, last_name):
    first = first_name.lower()
    last = last_name.lower()

    base_username_options = [
        f"{first}{last}",
        f"{first}.{last}",
        f"{first}_{last}",
        f"{first[0]}{last}",
        f"{last}{random.randint(10, 99)}",
        f"{first}{random.randint(100, 999)}",
    ]

    for base_username in base_username_options:
        username = base_username
        if not User.objects.filter(username=username).exists():
            return username

    # If all are taken, append random string
    while True:
        username = f"{first}{last}{''.join(random.choices(string.digits, k=3))}"
        if not User.objects.filter(username=username).exists():
            return username
