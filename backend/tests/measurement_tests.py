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
