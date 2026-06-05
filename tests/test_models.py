from models import User
from app import db


def test_user_creation(app):
    user = User(username="newuser", email="new@example.com")
    user.set_password("securepass")
    db.session.add(user)
    db.session.commit()
    assert user.id is not None


def test_password_hashing(app):
    user = User(username="hashuser", email="hash@example.com")
    user.set_password("mypassword")
    assert user.check_password("mypassword") is True
    assert user.check_password("wrong") is False


def test_password_not_in_plain(app):
    user = User(username="plainuser", email="plain@example.com")
    user.set_password("supersecret")
    assert "supersecret" not in user.password_hash
