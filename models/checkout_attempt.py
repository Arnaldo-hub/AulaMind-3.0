# models/checkout_attempt.py
from extensions import db

class CheckoutAttempt(db.Model):
    __tablename__ = 'checkout_attempts'
    id = db.Column(db.Integer, primary_key=True)