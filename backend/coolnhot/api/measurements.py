# -*- coding: UTF-8 -*-
from datetime import timedelta
from sqlalchemy import sql, cast

__author__ = 'quentingerome'

import flask
from . import blueprint
from ..models import Measurement, db
from .. import validators
from .. import helpers
import arrow


@blueprint.route('/measurements', methods=['GET'])
@validators.validate(
	start_at=validators.Arrow(),
	end_at=validators.Arrow(),
)
@helpers.crossdomain('*', create_request=False)
def get_measurements(start_at=None, end_at=None):
	if not start_at:
		start_at = arrow.utcnow().replace(days=-1).datetime
	q = Measurement.query.per_interval(start_at=start_at, end_at=end_at)
	results = db.session.execute(q)
	return flask.jsonify(**dict(
		success=True,
		items=[dict(created_at=x[0], temperature=x[1], humidity=x[2]) for x in results],
	))
