from dataclasses import dataclass


@dataclass
class RegisterData:
    name: str
    email: str
    password: str


@dataclass
class LoginData:
    email: str
    password: str