from flask import Flask
import connexion
import os

#app = Flask(__name__)
app = connexion.App(__name__, specification_dir='./')
#app.add_api("swagger.yaml")

flask_app = app.app

PASSWORD=os.getenv("DB_PASS")
PUBLIC_IP_ADDRESS =os.getenv("DB_IP")
DBNAME ="projects_v2"
PROJECT_ID ="purde-final-project"
INSTANCE_NAME ="project-db"
 
# configuration
flask_app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
flask_app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

from Project2 import routes
from Project2 import apiroutes
