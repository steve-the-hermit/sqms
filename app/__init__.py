from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask  import Flask

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'admin123'

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import main
    app.register_blueprint(main)

    return app
