import secrets
import uuid
from flask import Blueprint, make_response, redirect, render_template, request, url_for
from flask_jwt_extended import jwt_required

from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt, jwt_required, JWTManager,
    get_jwt_identity, set_access_cookies, unset_jwt_cookies, verify_jwt_in_request
)

from flask_jwt_extended.exceptions import NoAuthorizationError
from werkzeug.security import generate_password_hash, check_password_hash

from TokenUsedError import TokenUsedError
from authDb import authDb
users = Blueprint('users', __name__, template_folder='templates')

revoked_tokens = set()

@users.route('/signin', methods=['GET'])
def login():
    error = request.args.get('error','')
    return render_template('login.html', error = error)

@users.route('/logout', methods=['POST', 'GET'])
def logout():
    response = make_response(redirect(url_for('users.login'))) # or render_template(...)
    unset_jwt_cookies(response)
    return response

@users.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    if not email or not password:
        # Redirect to login with error
        response = redirect(url_for("users.login", error="Invalid username or password!"))
        response = make_response(response)
        unset_jwt_cookies(response)
        return response

    user = authDb.getCurrentActiveUser(email)
    if not user or not check_password_hash(user['password'], password + user['salt']):
        # Login failed — clear any old tokens and redirect with error
        response = redirect(url_for("users.login", error="Invalid username or password!"))
        response = make_response(response)
        unset_jwt_cookies(response)
        return response

    # Login successful — issue new tokens
    access_token = create_access_token(identity=user['fullname'])
    refresh_token = create_refresh_token(identity=user['fullname'], additional_claims={"jti": str(uuid.uuid4())})
    # Set the tokens in cookies
    response = make_response(redirect(request.args.get("next") or url_for("homepage")))
    _set_jwt_cookies(response, 'access_token_cookie', access_token)
    _set_jwt_cookies(response, 'refresh_token_cookie', refresh_token)

    return response

@users.route('/register', methods=['GET'])
def newUser():
    userid = request.args.get('userid')
    email = request.args.get('email')
    return render_template('register.html', userid = userid, existedUser = email)

@users.route('/register', methods=['POST'])
def register():
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
   
    if not fullname or not email or not password:
        return redirect(url_for('users.newUser', error="Please fill in all fields."))

    user = authDb.getCurrentUser(email)
    if not user:
      salt = secrets.token_urlsafe(16)
      hashed_password = generate_password_hash(password + salt)
      userid = authDb.createUser(fullname,email,salt,hashed_password)
    else:
        return redirect(url_for('users.newUser',userid = None ,email=email))   

    return redirect(url_for('users.newUser',userid = userid ,email=None))

@users.route('/active', methods=['POST'])
def activateUser():
    userid = request.form['userid']
    if not userid:
        return redirect(url_for('users.newUser', error="Sorry, We can't find this user in the system."))

    user = authDb.getCurrentUser(userid)
    if not user:
        return redirect(url_for('users.newUser', error="User not found."))

    authDb.activeUser(userid)
    return redirect(url_for('users.login'))

@users.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    jti = get_jwt()["jti"]  # Get unique token identifier
    if jti in revoked_tokens:
        raise handle_token_used()

    revoked_tokens.add(jti)
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity, additional_claims={"jti": str(uuid.uuid4())})
    response = make_response(redirect(request.args.get("next") or url_for("homepage")))
    set_access_cookies(response, access_token)
    set_access_cookies(response, refresh_token)
    return response

@users.errorhandler(NoAuthorizationError)
def handle_missing_token(e):
    return render_template('error.html', status_code=401, msg="You are not authorized to access this page."), 401

@users.errorhandler(TokenUsedError)
def handle_token_used(e):
    return render_template("error.html", status_code=401, msg="Your refresh token has already been used."), 401

def _set_jwt_cookies(response, key ,token):
    response.set_cookie(
        key,
        token,
        httponly=True,
        secure=False,  # set to True if using HTTPS
        samesite='Strict'
    )
