from flask import Blueprint

bp = Blueprint("health", __name__)  # pylint: disable=C0103

@bp.route('/healthz', methods=['GET'])
def heath():  # pylint: disable=C0116
    return ('Healthy\n', 200)
