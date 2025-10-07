import string
import random

from app.config import settings


class URLService:
    def __init__(self):
        self.base_url = settings.base_url

    def generate_short_code(self, length: int = 6):
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))
