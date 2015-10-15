import logging
from .errors import Invalid

log = logging.getLogger(__name__)

from functools import wraps

from flask import request, abort, g, make_response
from .schema import Schema, Validator

__all__ = ['validate', 'invalid']


def invalid(errors={}, api=False, force_text=False):
	formatted_errors = dict((f, unicode(e.msg) if hasattr(e, 'msg') else unicode(e)) for f, e in errors.iteritems())
	if api == False:
		abort(400)
	elif api == True:
		data = {'errors': formatted_errors}
		if force_text:
			data['success'] = False
		return make_response((data, 400, {'content-type': 'text/html' if force_text else 'application/json'}))
	else:
		return api(formatted_errors)


def validate(validators={}, post=[], api=False, jsonp=None, force_text=False, add_view_kwargs=False, **kwargs):
	if kwargs:
		validators, post = kwargs, []

	assert api == True or api == False or callable(api), '"api" is supposed to be a boolean or a callable'

	for name, validator in validators.items():
		if not isinstance(validator, Validator):
			validator = Validator(validator)
			validators[name] = validator

	schema = Schema(validators=validators, post_validators=post)

	def decorator(f):
		@wraps(f)
		def decorate(*base_args, **view_kwargs):
			# Gather all args we have into a single multidict
			args = request.args.copy()
			args.update(request.form)
			if request.get_json(silent=True):
				args.update(request.json)
			args.update(request.files)
			args.update(view_kwargs)

			new_args, error_args, extra_args = schema.validate(args)
			log.debug('Validate: %r -> %r / %r / %r', args, new_args, error_args, extra_args)
			g.validate_args, g.validate_error_args, g.validate_extra_args = new_args, error_args, extra_args
			if error_args:
				return invalid(error_args, api=api, force_text=force_text)

			try:
				if add_view_kwargs:
					view_kwargs.update(new_args)
					new_args = view_kwargs
				return f(*base_args, **new_args)
			except Invalid as e:
				error_values = {}
				if e.fields:
					for field in e.fields:
						error_values[field] = e
				else:
					error_values[e.field] = e
				return invalid(errors=error_values, api=api, force_text=force_text)
		return decorate
	return decorator
