"""
Validation Exceptions
=====================

.. autodata:: MESSAGES
"""
__all__ = ['Invalid']

#: Stock validation error messages
MESSAGES = {
	'missing-value': "Missing value",
	'mismatch':      "Field does not match",
	'invalid-int':   "Not a number",
	'invalid-date':  "Not a date",
	'invalid-json':  "Invalid JSON",
	'invalid-url':   "Invalid URL",
	'invalid-email': "Invalid E-mail address",
	'invalid':       "Invalid value",
	'not-found':     "Not found",
	'not-unique':    "Already exists",
}

class Invalid(Exception):
	"""
	The exception class used for all validation errors. It contains the `field` name that triggered the error
	and a `msg` attribute with the stock or custom error message.

	The `msgid` should be one of the keys in :data:`MESSAGES`.

	:param field: The field name that triggered this exception
	:type field: string

	:param fields: The fields' name that triggered this exception
	:type fields: list of string

	:param msgid: The message id to use if no `msg` is specified
	:type msgid: string
	
	:param msg: The optional message override
	:type msg: unicode string
	"""
	def __init__(self, field=None, msgid=None, msg=None, fields=None, **kwargs):
		super(Invalid, self).__init__(kwargs)
		self.field = field
		self.fields = fields
		self.msgid = msgid
		self.msg = msg or MESSAGES.get(msgid or 'invalid')

	def __repr__(self):
		return "Invalid(%r, %r)" % (self.fields or self.field, self.msg)
