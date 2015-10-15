"""
Post Validators
===============
"""
from .errors import Invalid

__all__ = ['PostValidator', 'FieldsMatch', 'RequireField', 'PostAssert', 'RequireFields']

class PostValidator(object):
	"""
	The base class for all post validators.
	"""
	def validate(self, values):
		"""
		Validate the given dict of values. The post validator can modify the dict in place if needed.

		:param values: The parameters to validate
		:type values: dict
		:raise: :exc:`~framework.validators.errors.Invalid`
		"""
		raise NotImplementedError

class FieldsMatch(PostValidator):
	"""
	Ensures that the two given fields have the same value.

	If both fields are missing they match, otherwise a python `!=` comparison is performed between the two values.

	:raise: :exc:`~framework.validators.errors.Invalid` if there is a mismatch in the values
	"""
	def __init__(self, field, other_field):
		self.field, self.other_field = field, other_field

	def validate(self, values):
		# Sentinel value
		missing1 = object()
		missing2 = object()

		field = values.get(self.field, missing1)
		other_field = values.get(self.other_field, missing2)

		if field is missing1 and other_field is missing2:
			# Both fields were not present at all, that's ok
			return

		if field != other_field:
			raise Invalid(field=self.field, mismatch=(self.field, self.other_field), msgid="mismatch")

class RequireField(PostValidator):
	"""
	Ensures that if a given field is present, another field also is present.

	The field is considered present if in the values and not in one of the `missing_values`.

	:param field: The field that should be present
	:param if_field: The field that is checked to determine if `field` should be present
	:param missing_values: The list of values that are considered to be missing
	:type missing_values: tuple
	:raise: :exc:`~framework.validators.errors.Invalid` if the required field is not present.
	"""
	def __init__(self, field, if_field, missing_values=('', None)):
		self.field, self.if_field, self.missing_values = field, if_field, missing_values

	def validate(self, values):
		if self.if_field not in values or values[self.if_field] in self.missing_values:
			# The if_field is either not present, or considered missing
			return

		if self.field not in values or values[self.field] in self.missing_values:
			# The field is either not present, or considered missing
			raise Invalid(field=self.field, msgid="missing-value")


class RequireFields(PostValidator):
	def __init__(self, fields, missing_values=('', None)):
		self.fields, self.missing_values = fields, missing_values
		super(RequireFields, self).__init__()

	def validate(self, values):
		def checkEqualIvo(lst):
			return not lst or lst.count(lst[0]) == len(lst)

		check_fields = map(lambda f: (f, f not in values or values[f] in self.missing_values), self.fields)  # False means that field is filled

		if not checkEqualIvo(zip(*check_fields)[1]):
			missing_fields = filter(lambda (f, v): v is True, check_fields)
			raise Invalid(fields=zip(*missing_fields)[0], msgid="missing-value")


class PostAssert(PostValidator):
	"""
	Calls a function with the parameters and raise an exception if the function returns nothing.

	:param field: The field name to associate this post validator to
	:param fn: The assertion function
	:raise: :exc:`~framework.validators.errors.Invalid` if the function returned nothing
	"""
	def __init__(self, field, fn):
		self.field, self.fn = field, fn

	def validate(self, values):
		if not self.fn(values):
			raise Invalid(field=self.field, msgid="invalid")
