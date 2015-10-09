from . import CoolnHotAppTestCase
from decimal import Decimal

class TrivialTests(CoolnHotAppTestCase):
	def test_basic(self):
		self.assertTrue(True)

	def test_create_reading(self):
		from coolnhot.models import Measurement
		reading = Measurement(temperature=Decimal("22"), humidity=Decimal("45"))
		self.db.session.add(reading)
		self.db.session.flush()
		self.assertTrue(Measurement.query.count() == 1)

		self.db.session.delete(Measurement.query.first())
		self.db.session.flush()
		self.assertTrue(Measurement.query.count() == 0)
