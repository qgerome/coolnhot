# -*- coding: UTF-8 -*-

__author__ = 'quentingerome'

import flask
from . import blueprint
from ..models import Measurement
from .. import validators
from .. import helpers


@blueprint.route('/measurements/avg', methods=['GET', 'OPTIONS'])
@validators.validate(
	start_at=validators.Arrow(),
    end_at=validators.Arrow()
)
@helpers.crossdomain('*', create_request=False)
def average(start_at=None, end_at=None):
	(avg_temperature, avg_rel_humidity) = Measurement.query.avg(start_at=start_at and start_at.datetime, end_at=end_at and end_at.datetime)

	return flask.jsonify(**dict(
		success=True,
		average=dict(
			temperature=avg_temperature,
			rel_humidity=avg_rel_humidity
		)
	))
