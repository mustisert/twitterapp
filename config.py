import os
import sqlalchemy

USERNAME = os.environ.get('USERNAME') or 'root' # Change this to your username in production
PASSWORD = os.environ.get('PASSWORD') or 'ares' # Change this to your password in production
DBNAME = os.environ.get('DBNAME') or 'twitter' # Change this to your database name in production
PROJECT_ID = os.environ.get('PROJECT_ID') or 'twitter-clone-project' # Change this to your project id in production
INSTANCE_NAME = os.environ.get('INSTANCE_NAME') or 'twitter-clone' # Change this to your instance name in production
PUBLIC_IP_ADDRESS = os.environ.get('PUBLIC_IP_ADDRESS') or '34.67.134.75' # Change this to your public ip address in production
CONNECTION_NAME = "expanded-league-381220:us-central1:twitter-clone-project"
PORT = 3306

URI = sqlalchemy.engine.url.URL.create(
    drivername="mysql+pymysql",
    username=USERNAME,
    password=PASSWORD,
    host=PUBLIC_IP_ADDRESS,
    database=DBNAME,
    port=PORT
)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key' # Change this to a more secure secret key in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False