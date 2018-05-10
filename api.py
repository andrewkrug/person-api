import logging
from flask import Flask
from flask import jsonify
from flask_cors import cross_origin
from flask_swagger import swagger
from flask.views import MethodView

from person_api.idp import requires_auth
from person_api.idp import requires_scope
from person_api.exceptions import AuthError
from person_api.models.v1.connection import ConnectionAPI
from person_api.models.v1.profile import ProfileAPI
from person_api import __version__

app = Flask(__name__)


logger = logging.getLogger(__name__)


connection_view = ConnectionAPI.as_view('connection')
profile_view = ProfileAPI.as_view('profile')
app.add_url_rule('/v1/connection/', view_func=connection_view, methods=["GET"])
app.add_url_rule('/v1/connection/<user_email>', view_func=connection_view, methods=["GET"])
app.add_url_rule('/v1/connection/?', view_func=connection_view, methods=["GET"])
app.add_url_rule('/v1/profile/<user_id>', view_func=profile_view, methods=["GET", "POST"])
app.add_url_rule('/v1/profile/', view_func=profile_view, methods=["GET"])
app.add_url_rule('/v1/profile/?', view_func=profile_view, methods=["GET"])


@app.route("/spec")
def spec():
    return jsonify(swagger(app, from_file_keyword='swagger_from_file'))

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


# This doesn't need authentication
@app.route("/version")
@cross_origin(headers=['Content-Type', 'Authorization'])
def version():
    response = __version__
    return jsonify(message=response)


# This doesn't need authentication
@app.route("/api/public")
@cross_origin(headers=['Content-Type', 'Authorization'])
def public():
    response = "Hello from a public endpoint!"
    return jsonify(message=response)


# This does need authentication
@app.route("/api/private", methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def private():
    response = "Hello from a private endpoint!"
    return jsonify(message=response)


# This needs authentication and scope
@app.route("/api/private-scoped", methods=['GET', 'POST'])
@cross_origin(headers=["Content-Type", "Authorization"])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
@requires_auth
def private_scoped():
    """A valid Access Token and an appropriate scope are required to access this route
    """
    if requires_scope("read:profile"):
        response = "Hello from a scoped private endpoint!"
        return jsonify(message=response)
    else:
        raise AuthError({
            "code": "Unauthorized",
            "description": "Scope not matched.  Access Denied."
        }, 403)
