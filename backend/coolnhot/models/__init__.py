from dateutil.relativedelta import relativedelta
from flask.ext.sqlalchemy import BaseQuery

from sqlalchemy import sql
from datetime import datetime
from ..extensions import db
import math


class MeasurementQuery(BaseQuery):
	def avg(self, start_at=None, end_at=None):
		if not end_at: end_at = datetime.utcnow()
		if not start_at: start_at = end_at - relativedelta(minutes=30)

		avg = db.session.query(sql.func.avg(Measurement.temperature), sql.func.avg(Measurement.humidity)).filter(Measurement.created_at.between(start_at, end_at)).first()
		if avg[0] and avg[1]:
			return dict(temperature=0.5 * math.floor(2.0 * avg[0]), humidity=0.5 * math.floor(2.0 * avg[1]))

	def per_interval(self, interval=300, start_at=None, end_at=None):
		col = sql.func.datetime((sql.func.strftime('%s', Measurement.created_at) / interval) * interval, 'unixepoch')
		q = sql.select([col, sql.func.avg(Measurement.temperature), sql.func.avg(Measurement.humidity)]).group_by(col)
		if start_at:
			q = q.where(Measurement.created_at >= start_at)
		if end_at:
			q = q.where(Measurement.created_at < end_at)
		return q


class Measurement(db.Model):
	__tablename__ = "measurements"

	query_class = MeasurementQuery

	id = db.Column(db.Integer, autoincrement=True, primary_key=True, index=True, nullable=False)
	temperature = db.Column(db.Float(), nullable=False)
	humidity = db.Column(db.Float(), nullable=False)
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	def __init__(self, temperature, humidity, *args, **kwargs):
		self.temperature = temperature
		self.humidity = humidity
		super(Measurement, self).__init__(*args, **kwargs)

	def __repr__(self):
		return "<Measurement(id={self.id}, temperature={self.temperature}, humidity={self.humidity})>".format(self=self)
