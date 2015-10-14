# -*- coding: UTF-8 -*-

__author__ = 'quentingerome'

import flask
from flask import request
import arrow
from . import blueprint
from ..models import Measurement

@blueprint.route('/measurements/avg', methods=['GET'])
def average():
	end_at = arrow.get(request.args.get('end_at'))
	start_at = request.args.get('start_at')
	if start_at:
		start_at = arrow.get(start_at)
	else:
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
