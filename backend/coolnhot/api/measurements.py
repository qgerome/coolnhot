# -*- coding: UTF-8 -*-

__author__ = 'quentingerome'

import flask
from . import blueprint
from ..models import Measurement
from .. import validators
from .. import helpers
import arrow


def jsonify_measurement(measurement):
	return dict(
		temperature=measurement.temperature,
	    humidity=measurement.humidity,
	    created=measurement.created_at
	)

@blueprint.route('/measurements/avg', methods=['GET', 'OPTIONS'])
@validators.validate(
	start_at=validators.Arrow(),
    end_at=validators.Arrow()
)
@helpers.crossdomain('*', create_request=False)
def average(start_at=None, end_at=None):
	measurement = Measurement.query.avg(start_at=start_at and start_at.datetime, end_at=end_at and end_at.datetime)

	return flask.jsonify(**dict(
		success=True,
		average=measurement
	))


@blueprint.route('/measurements', methods=['GET'])
@validators.validate(
	page=validators.Int(),
	start_at=validators.Arrow(),
	end_at=validators.Arrow(),
	items_per_page=validators.Int(),
)
def get_measurements(page=1, start_at=None, end_at=None, items_per_page=50):
	q = Measurement.query
	if start_at:
		q = q.filter(Measurement.created_at >= start_at.datetime)
	if end_at:
		q = q.filter(Measurement.created_at <= end_at)

	pagination = q.paginate(page, per_page=items_per_page)
	return flask.jsonify(**dict(
		success=True,
		items=[jsonify_measurement(x) for x in pagination.items],
		total=pagination.total,
		has_next=pagination.has_next
	))