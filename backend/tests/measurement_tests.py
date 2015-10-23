# -*- coding: UTF-8 -*-
import json
from flask import url_for

__author__ = 'quentingerome'

import logging
from . import CoolnHotAppTestCase
from coolnhot.models import Measurement
from datetime import datetime
import random
from dateutil.relativedelta import relativedelta

log = logging.getLogger(__name__)


class MeasurementTestCase(CoolnHotAppTestCase):
	def create_measurement(self, temperature=None, humidity=None, created_at=None):
		m = Measurement(
			temperature=temperature or random.randint(-100, 300) / 10,
			humidity=humidity or random.randint(200, 800) / 10,
			created_at=created_at
		)
		self.session.add(m)
		return m

	def _create_fixtures(self):
		super(MeasurementTestCase, self)._create_fixtures()

	def test_create(self):
		self.create_measurement()
		self.session.commit()
		self.assertTrue(Measurement.query.count() == 1)

		self.session.delete(Measurement.query.first())
		self.session.commit()
		self.assertTrue(Measurement.query.count() == 0)

	def test_avg(self):
		now = datetime.utcnow()
		measurements = [
			Measurement(5.5, 43, created_at=now),
			Measurement(6.4, 45, created_at=now - relativedelta(minutes=5)),
			Measurement(7, 50, created_at=now - relativedelta(minutes=10)),
		]

		map(self.session.add, measurements)
		self.session.commit()

		avg = Measurement.query.avg(now - relativedelta(minutes=11), now + relativedelta(seconds=5))
		self.assertEquals(avg, (6.3, 46))

	def test_get_first_page(self):
		measurements = [self.create_measurement() for _ in range(10)]
		self.session.commit()
		self.session.close()
		with self.app.test_client() as client:
			rv = self.assertOkJson(client.get(url_for('api.get_measurements'), data=dict(page=1, items_per_page=5)))
			content = json.loads(rv.data)
			self.assertTrue(content['has_next'] is True)

			rv = self.assertOkJson(client.get(url_for('api.get_measurements'), data=dict(page=2, items_per_page=5)))
			content = json.loads(rv.data)
			self.assertTrue(content['has_next'] is False)