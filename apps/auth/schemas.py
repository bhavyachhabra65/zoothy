from dataclasses import dataclass


@dataclass
class RegisterData:
    name: str
    email: str
    password: str

