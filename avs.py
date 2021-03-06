"""
resolve avs connection
should be redirect with flask blueprint
"""

from requests_oauthlib import OAuth2Session

from flask import Blueprint, request, redirect, session, url_for
from flask.json import jsonify

import os
import json

avs_service = Blueprint('avs_service', __name__)

# This information is obtained upon registration of a amazon avs product
# should be contained in deploy.json file for safety
with open('deploy.json') as file:
    _deploy = json.load(file)
    client_id = _deploy['client_id']
    client_secret = _deploy['client_secret']
    product_id = _deploy['product_id']
    product_sn = _deploy['product_sn']
    redirect_uri = _deploy['redirect_uri']

# api url from https://developer.amazon.com/public/solutions/alexa/alexa-voice-service/docs/authorizing-your-alexa-enabled-product-from-a-website
authorization_base_url = 'https://www.amazon.com/ap/oa'
token_url = 'https://api.amazon.com/auth/o2/token'

@avs_service.route("/login")
def index():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider:
    amazon avs with Authorization Code Grant
    """
    # construct scope_data
    _scope_data = {
        "alexa:all": {
            "productID": product_id,
            "productInstanceAttributes": {
                "deviceSerialNumber": product_sn
            }
        }
    }

    # state will be generated by default
    # TODO: check stored session before initiate a new one
    avs = OAuth2Session(client_id, scope='alexa:all', redirect_uri=redirect_uri)
    authorization_url, state = avs.authorization_url(authorization_base_url, scope_data=json.dumps(_scope_data))

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step  2: User authorization, this happens on the provider.

@avs_service.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    avs = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    token = avs.fetch_token(token_url,authorization_response=request.url,client_secret=client_secret)

    # At this point you can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('/'))


# @app.route("/profile", methods=["GET"])
# def profile():
#     """Fetching a protected resource using an OAuth 2 token.
#     """
#     github = OAuth2Session(client_id, token=session['oauth_token'])
#     return jsonify(github.get('https://api.github.com/user').json())


if __name__ == "__main__":
    import ssl
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(avs_service, url_prefix='/avs')

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('server.crt', 'server.key')
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"

    app.secret_key = os.urandom(24)
    app.run(host='localhost', port=5000, debug=True, ssl_context=context)
