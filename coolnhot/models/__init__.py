from datetime import datetime
from ..extensions import db


class Measurement(db.Model):
	__tablename__ = "measurements"

	id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True, nullable=False)
	temperature = db.Column(db.Float(), nullable=False)
	humidity = db.Column(db.Float(), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	def __init__(self, temperature, humidity):
		self.temperature = temperature
		self.humidity = humidity
		super(Measurement, self)

	def __repr__(self):
		return "<Measurement(id={self.id}, temperature={self.temperature}, humidity={self.humidity})>".format(self=self)
