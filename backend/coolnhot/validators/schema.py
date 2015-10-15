"""
Validation Schema and Validators
================================

.. autoclass:: Schema
   :members:

.. autoclass:: Validator
   :members:

.. autoclass:: CheckboxValidator

.. autoclass:: FileValidator
"""
import logging
log = logging.getLogger(__name__)

from werkzeug import MultiDict

from .errors import Invalid
from .filters import StripEmpty, Strip, Default, File, Bool

__all__ = ['Schema', 'Validator', 'FileValidator', 'CheckboxValidator']

NO_VALUE = object()

class Validator(object):
	"""
	Validate a list of strings against the filter chain passed in argument.

	If `field` is specified, the value list will be extracted from that field name instead of the name associated to the validator.
	This allows to have a different field name in a form than the resulting argument::

	    >>> s = Schema(validators={'number': Validator(validators.Int(), field='id')})
	    >>> s.validate({'id': 3})
	    {'number': 3}, {}, {}
	    >>> s.validate({'id': 'a'})
	    {}, {'id': Invalid(...)}, {}

	If `strip` is specified, the value list will be stripped prior to being passed to the filters.
	
	if `strip_empty` is specified, the value list will be pruned of any empty string prior to being passed to the filters.

	Internally `strip` and `strip_empty` will prepend the `~framework.validators.filters.Strip` and `~framework.validators.filters.StripEmpty` filters
	to the given chain and the `~framework.validators.filters.Default` filter is appended to the filter chain with the given default value
	

	:param filters: The filter (or filter chain) to use
	:type filters: :class:`~framework.validators.filters.Filter`

	:param field: The field from the parameters this validator is applied to
	:type field: string

	:param strip: Strip the input values before processing
	:type strip: bool

	:param strip: Remove empty strings from input values before processing
	:type  strip_empty: bool

	:param aslist: Whether to expect a list result or not. When aslist is False (the default) then the default param can be provided.

	:param default: The default value to be returned when the filtered value list is empty (with aslist=False).
	"""
	def __init__(self, filters=[], field=None, strip=True, strip_empty=True, default=NO_VALUE, aslist=False, startswith=None):
		self.field = field
		self.aslist = aslist
		self.startswith = startswith

		if strip_empty:
			filters = StripEmpty() | filters
		if strip:
			filters = Strip() | filters

		if aslist and default is not NO_VALUE:
			raise Exception('Cannot provide a default for a list validator, will always return a (possibly empty) list')
		elif not aslist:
			filters = filters | Default([default])

		self.filters = filters

	def validate(self, value=[]):
		value = self.filters.run(value)
		if self.aslist:
			return value
		return value[0]

class FileValidator(Validator):
	def __init__(self, filters=None, field=None, aslist=False):
		super(FileValidator, self).__init__(filters=File() | filters, field=field, strip=False, strip_empty=False, aslist=aslist)

class CheckboxValidator(Validator):
	def __init__(self, filters=None, field=None, aslist=False):
		super(CheckboxValidator, self).__init__(filters=Bool() | filters, field=field, strip=True, strip_empty=False, aslist=aslist, default=False)

class Schema(object):
	"""
	A validation schema is used to :meth:`validate` a dict of parameters against a set of validators and post validators.

	Each validator should be an instance of :class:`Validator`.

	For the exact validation rules, see the :meth:`validate` method.

	:param validators: The dict mapping parameter names to validator instances.
	:type validators: dict
	:param post_validators: The list of post validators (see :mod:`framework.validators.post`)
	:type post_validators: list
	"""
	def __init__(self, validators={}, post_validators=[]):
		self.validators = validators
		self.post_validators = post_validators

		# Assign missing field names from the validators dict
		for n, v in self.validators.iteritems():
			if not v.field:
				v.field = n

	def validate(self, values):
		"""
		Validate the given dict of values against the validators and post validators of this schema. This dict should be a
		dict with list values or an instance of a werkzeug `MultiDict`.

		Any parameter that is not explicitely validated will be returned as extra values.

		If a parameter is found it is passed to the validator's :meth:`~framework.validators.schema.Validator.validate` method that will either
		return a valid output or trigger a validation error.

		After individual validators are processed, the resulting valid parameters are passed to each `post_validators`.
		Each post validator can change the resulting values or trigger a validation error.

		When a validation error is triggered, an entry is added to the error dict mapping the field name that produced the error
		to an instance of :exc:`~framework.validators.errors.Invalid` (containing the error message and error value).

		After those steps, the validated values, the validation errors and the extra values dicts are returned.

		:param values: The dict of values to validate against this schema
		:type values: dict

		:return: The dict of validated values, The dict of error messages, The dict of extra values
		:rtype: a tuple (dict, dict)
		"""

		# Ensure we have a **new** dict with lists as values if it's a werkzeug MultiDict
		#  we are going to pop values from it...
		values = MultiDict(values)

		new_values = {}
		error_values = {}

		for name, validator in self.validators.iteritems():
			# Determine the key to fetch from the received values
			field = validator.field or name
			# Get the list of values, which may be empty if the field was not present or contain some values
			if validator.startswith:
				value = [(x, values[x]) for x in values.iterkeys() if x.startswith(validator.startswith)]
			else:
				value = values.poplist(field)

			try:
				value = validator.validate(value)
				if value is not NO_VALUE:
					new_values[name] = value
			except Invalid, e:
				error_values[e.field or field] = e

		# Whatever's left in the values dict will be returned as is
		extra_values = values

		for validator in self.post_validators:
			try:
				validator.validate(new_values)
			except Invalid, e:
				if e.fields:
					for f in e.fields:
						error_values[f] = e
				else:
					error_values[e.field] = e

		return new_values, error_values, extra_values
