from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

   
   # from .authog import auth as auth2
    #app.register_blueprint(authog, url_prefix='/')


    return app