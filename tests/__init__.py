from unittest import TestCase
from coolnhot.factory import create_app
from coolnhot.extensions import db
from . import settings
from .utils import FlaskTestCaseMixin

# from .factories import UserFactory



class CoolnHotTestCase(TestCase):
	pass


class CoolnHotAppTestCase(FlaskTestCaseMixin, CoolnHotTestCase):

	def _create_app(self, *args, **kwargs):
		self.app = create_app(*args, **kwargs)

	def _create_fixtures(self):
		pass

	def setUp(self):
		super(CoolnHotAppTestCase, self).setUp()
		self._create_app(__name__, settings)
		self.db = db
		self.client = self.app.test_client()
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.db.create_all()
		self._create_fixtures()
		self._create_csrf_token()

	def tearDown(self):
		super(CoolnHotAppTestCase, self).tearDown()
		self.db.drop_all()
		self.app_context.pop()
