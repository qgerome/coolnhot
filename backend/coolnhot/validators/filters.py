"""
Validation Filters
==================
"""
import logging
from dateutil.parser import parse
from flask import g

log = logging.getLogger(__name__)

import werkzeug
import json
import re
import arrow


def _re_or(*args):
	return '(?:' + '|'.join(args) + ')'

# From RFC2396
_rfc_alphanum = r'[a-zA-Z0-9]'
_rfc_mark = r'[-_\.!~*\'\(\)]'
_rfc_reserved = r';/?:@&=+$,'
_rfc_escaped = r'(?:%[0-9a-fA-F]{2})'
_rfc_unreserved = _re_or(_rfc_alphanum, _rfc_mark)
_rfc_userinfo = _re_or(_rfc_unreserved, _rfc_escaped, r'[;:&=+$,]') + '+'

# Written based on RFC but not strict
_re_ipv6 = r'((::(X){1,7})|((X){1,7}::)|((X:){1,6}(X)?(:X){1,6}))' \
	.replace('(', '(?:') \
	.replace('X', '[0-9a-fA-F]{1,4}')
_re_host_ipv6 = '\[' + _re_ipv6 + '\]'
_re_host_ipv4 = r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
_re_host_name = r'(?:[a-zA-Z0-9-_]+\.)+[a-zA-Z]{2,6}'


# URL parts
_re_scheme = r'https?://'
_re_user = '(?:' + _rfc_userinfo + '@)?'
_re_host = _re_or(_re_host_name, _re_host_ipv4, _re_host_ipv6)
_re_port = r'(?::[0-9]{1,5})?'
_re_therest = r"(?:\/[-_.!~*'()a-zA-Z0-9;\/?:\@&=+\$,%#\{\}]*)?"


_re_href = _re_scheme + _re_user + _re_host + _re_port + _re_therest

HREF_VALIDATE_RE = re.compile('^%s$' % _re_href, re.I)
HREF_FIND_RE = re.compile('(%s)' % _re_href, re.I)

# From http://www.regular-expressions.info/email.html
_re_mail = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"

MAIL_VALIDATE_RE = re.compile('^%s$' % _re_mail, re.I)
MAIL_FIND_RE = re.compile('(%s)' % _re_mail, re.I)

HREF_OR_MAIL_FIND_RE = re.compile('(?:(?P<href>%s)|(?P<mail>%s))' % (_re_href, _re_mail), re.I)


from .errors import Invalid

__all__ = [
	'Filter', 'Strip', 'StripEmpty', 'Default', 'Required', 'String', 'Int', 'Bool', 'Date', 'Arrow',
	'Json', 'Url', 'Email', 'File', 'Regex',
	'Id', 'Query', 'UniqueQuery', 'Assert', 'G',
]

class Filter(object):
	"""
	The base class for all filters. If you need to define your own filter you must inherit from this class and define the :meth:`filter` method.

	A filter basically takes a value list as input and either returns another value list or raises an :exc:`~framework.validators.errors.Invalid` exception.

	Filters can be chained using the `|` operator to pipe the output of one filter to the next one::

	    validators.Int() | validators.Query(...) | ....

	* The positional parameters passed to the constructor are set as instance attributes using the names from the `args` class attribute
	* The keyword parameters passed to the constructor are set as instance attributes.

	For example::

	    >>> class Foo(Filter):
	    >>>    args = ['a', 'b']
	    >>> f = Foo(1, 2, test=3)
	    >>> f.a
	    1
	    >>> f.b
	    2
	    >>> f.test
	    3

	All filters take a `msg` keyword argument that overrides the default error message for that filter.

	:param msg: The custom error message to display in case of validation error
	:type msg: unicode string
	"""

	msg = None
	args = []

	def __init__(self, *args, **kwargs):
		if len(args) > len(self.args):
			raise Exception('Too many arguments: %r' % (args[len(self.args):],))

		for i, arg in enumerate(args):
			setattr(self, self.args[i], arg)

		for arg in self.args:
			if not hasattr(self, arg):
				raise Exception('Missing "%s" argument' % arg)

		for k, v in kwargs.iteritems():
			setattr(self, k, v)

		self.chain = [self]

	def __len__(self):
		return len(self.chain)

	def __or__(self, other):
		if other is None or other == []:
			return self

		self.chain.extend(other.chain)
		other.chain = self.chain
		return other

	def run(self, values):
		for f in self.chain:
			values = f.filter(values)
		return values

	def filter(self, values):
		return [self.filter_value(v) for v in values]

	def filter_value(self, value):
		raise NotImplementedError

class Strip(Filter):
	def filter_value(self, v):
		if isinstance(v, basestring):
			return v.strip()
		return v

class StripEmpty(Filter):
	def filter(self, values):
		return [v for v in values if v is not None]

class Default(Filter):
	args = ['default']
	def filter(self, values):
		if values:
			return values
		else:
			return self.default

class Required(Filter):
	def filter(self, values):
		if values:
			return values
		else:
			raise Invalid(value=values, msgid="missing-value", msg=self.msg)

class File(Filter):
	"""
	Ensures that the given input value is an instance of a werkzeug file wrapper.

	:raise: :exc:`~framework.validators.errors.Invalid`
	"""
	def filter(self, values):
		return [v for v in values if isinstance(v, werkzeug.FileStorage) and v.filename and not (v.content_type == 'application/octet-stream' and v.filename == '<fdopen>')]

class String(Filter):
	"""
	String filter, basically does nothing by default unless `lower` is set to `True`.

	:param lower: Whether to lowercase the input string
	:type lower: bool
	"""
	lower = False
	def filter_value(self, v):
		if self.lower:
			return v.lower()
		return v

class Int(Filter):
	"""
	Convert a string representation of an int to a python `int`.

	:raise: :exc:`~framework.validators.errors.Invalid`
	"""
	def filter_value(self, v):
		try:
			return int(v) if v else 0
		except ValueError:
			raise Invalid(value=v, msgid="invalid-int", msg=self.msg)

class Bool(Filter):
	"""
	Convert a string representation of a boolean to a python `bool`.

	Browser have a special way of defining the value of such checkboxes:

	* If it's not present, then it should be `False`
	* If it's present, but not equal to 'falsy strings' then it should be `True`
	* If it's present and equal to 'falsy strings' then it should be `False`

	The 'falsy strings' are `false`, `off`, `0`, `no` (case insensitive)
	"""

	falsy_strings = ('false', 'off', '0', 'no')

	def filter_value(self, v):
		if isinstance(v, bool):
			return v
		return v and v.lower() not in self.falsy_strings or False


class Date(Filter):
	"""
	Convert a string representation of a date to a python `datetime`.

	The recognized format is `%Y-%m-%d`.

	:raise: :exc:`~framework.validators.errors.Invalid`
	"""
	def filter_value(self, v):
		try:
			return v and parse(v) or None
		except ValueError:
			raise Invalid(value=v, msgid="invalid-date", msg=self.msg)

class Arrow(Filter):
	"""
	Convert a string representation of a date to a python `datetime`.

	:raise: :exc:`~framework.validators.errors.Invalid`
	"""
	def filter_value(self, v):
		try:
			return arrow.get(v)
		except ValueError:
			raise Invalid(value=v, msgid="invalid-date", msg=self.msg)

class Json(Filter):
	"""
	Convert a string representation of a json value to its equivalent python value (using `json.loads()`).

	:raise: :exc:`~framework.validators.errors.Invalid`
	"""
	def filter_value(self, v):
		try:
			return json.loads(v)
		except ValueError:
			raise Invalid(value=v, msgid="invalid-json", msg=self.msg)

class Url(Filter):
	"""
	Ensures that the given string is a valid url according to whatever-lib's definition of it.

	If it doesn't start with `https?://`, then `http://` is automatically prepended.

	:raise: :exc:`~framework.validators.errors.Invalid`
	"""
	proto_re = re.compile(r'^https?://.*')
	def filter_value(self, v):
		if not self.proto_re.match(v):
			value = u'http://' + v

		if not HREF_VALIDATE_RE.match(v):
			raise Invalid(value=v, msgid="invalid-url", msg=self.msg)
		return v

class Email(Filter):
	"""
	Ensures that the given string is a valid email address according to whatever-lib's definition of it.

	:raise: :exc:`~framework.validators.errors.Invalid`
	"""
	def filter_value(self, v):
		if not MAIL_VALIDATE_RE.match(v):
			raise Invalid(value=v, msgid="invalid-email", msg=self.msg)
		return v

class Regex(Filter):
	"""
	Ensures that the given string matches the given regex (using `re.match`).

	:param re: The pattern used to match the input string
	:type re: string

	:raise: :exc:`~framework.validators.errors.Invalid`
	"""
	args = ['re']
	def filter_value(self, v):
		if not re.match(self.re, v):
			raise Invalid(value=v, msgid="invalid", msg=self.msg)
		return v

class Id(Filter):
	"""
	Get an object from the database using the input value as primary key.
	
	Internally `kls.query.get(value)` is used to perform the query.

	:param kls: The class to query
	:type kls: a sqlalchemy-mapped class
	:raise: :exc:`~framework.validators.errors.Invalid` if the query returned no result.
	"""
	args = ['kls']
	lock = False
	def filter_value(self, v):
		q = self.kls.query
		if self.lock:
			q = q.with_lockmode('update')
		o = q.get(v)
		if not o:
			raise Invalid(value=v, msgid="not-found", msg=self.msg)
		return o

class Query(Filter):
	"""
	Calls the given function with the input value and return its output.

	:param fn: The function to query
	:type fn: callable
	:raise: :exc:`~framework.validators.errors.Invalid` if there was no result from the given function.
	"""
	args = ['fn']
	def filter_value(self, v):
		o = self.fn(v)
		if not o:
			raise Invalid(value=v, msgid="not-found", msg=self.msg)
		return o

class UniqueQuery(Filter):
	"""
	Calls the given function with the input value and ensures that it returns nothing, then return the original value.
	
	:param fn: The function to query
	:type fn: callable
	:raise: :exc:`~framework.validators.errors.Invalid` if the given function returned something.
	"""
	args = ['fn']
	def filter_value(self, v):
		o = self.fn(v)
		if o:
			raise Invalid(value=v, msgid="not-unique", msg=self.msg)
		return v

class Assert(Filter):
	"""
	Calls the given function with the input value and ensures that it returns something, then return the original value.

	:param fn: The function to query
	:type fn: callable
	:raise: :exc:`~framework.validators.errors.Invalid` if the given function returned nothing.
	"""
	args = ['fn']
	def filter_value(self, v):
		if not self.fn(v):
			raise Invalid(value=v, msgid="invalid", msg=self.msg)
		return v

class G(Filter):
	"""
	Get a variable inside the g object of flask.Required

	:param val:
		attribute to get from g (e.g: 'identity.user')
	:type val:
		str
	"""

	args = ['field']

	def filter_value(self, value):
		def recurs_getattr(o, attrs):
			return attrs and o or recurs_getattr(getattr(o, attrs[0]), attrs[1:])

		return recurs_getattr(g, self.field.split('.'))