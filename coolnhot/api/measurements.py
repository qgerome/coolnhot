# -*- coding: UTF-8 -*-

__author__ = 'quentingerome'

import flask
from flask import request
import arrow
from . import blueprint
from ..models import Measurement
from .. import validators


@blueprint.route('/measurements/avg', methods=['GET'])
@validators.validate(
	start_at=validators.Arrow(),
    end_at=validators.Arrow()
)
def average(start_at=None, end_at=None):
	if not end_at:
		end_at = arrow.utcnow()
	if not start_at:
		start_at = arrow.get(end_at)
		start_at.replace(minutes=10)

	(avg_temperature, avg_rel_humidity) = Measurement.query.avg(start_at=start_at.datetime, end_at=end_at.datetime)

	return flask.jsonify(**dict(
		success=True,
		average=dict(
			temperature=avg_temperature,
			rel_humidity=avg_rel_humidity
		)
	))
