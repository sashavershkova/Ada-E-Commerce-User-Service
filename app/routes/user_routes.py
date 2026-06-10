from ..db import db
from ..models.user import User
from flask import Blueprint, request, Response, abort, make_response
from ..utilities import create_model, get_models_with_filters, validate_model, update_model, get_user_by_email

bp = Blueprint("users_blueprint", __name__, url_prefix="/users")


@bp.post("/")
def create_user():
    request_body = request.get_json()

    try:
        new_user = create_model(User, request_body)
    except KeyError as e:
        abort(make_response({"message": f"Invalid: Missing key ({e.args[0]})"}, 400))
    except Exception:
        abort(make_response({"message": f"An account with email ({request_body['email']}) already exists."}, 409))

    return new_user.to_dict(), 201


@bp.get("/")
def get_all_users():
    return get_models_with_filters(User, request.args)


@bp.get("/<id>")
def get_single_user(id):
    try:
        user = validate_model(User, id)
    except ValueError as e:
        abort(make_response({"message": str(e)}, 400))
    except LookupError as e:
        abort(make_response({"message": str(e)}, 404))

    return user.to_dict()


@bp.get("/email")
def get_single_user_by_email():
    email = request.args.get("email")

    try:
        user = get_user_by_email(email)
    except RuntimeError as e:
        abort(make_response({"message": str(e)}, 500))
    except LookupError as e:
        abort(make_response({"message": str(e)}, 404))

    return user.to_dict()


@bp.put("/<id>")
def update_user(id):
    try:
        user = validate_model(User, id)
    except ValueError as e:
        abort(make_response({"message": str(e)}, 400))
    except LookupError as e:
        abort(make_response({"message": str(e)}, 404))

    request_body = request.get_json()
    update_model(user, request_body)

    return Response(status=204, mimetype="application/json")


@bp.delete("/<id>")
def delete_user(id):
    try:
        user = validate_model(User, id)
    except ValueError as e:
        abort(make_response({"message": str(e)}, 400))
    except LookupError as e:
        abort(make_response({"message": str(e)}, 404))

    db.session.delete(user)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@bp.get('/health')
def health():
    return {'status': 'healthy', 'version': '1.0.1'}, 200