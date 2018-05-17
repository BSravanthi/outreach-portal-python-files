
# DB URI
# example DB URI:
# mysql+oursql://scott:tiger@localhost/mydatabase
# postgresql+psycopg2://scott:tiger@localhost/mydatabase
SQLALCHEMY_DATABASE_URI = 'mysql+oursql://<userid>:<password>@<servername>/<db_name>'
# example
# SQLALCHEMY_DATABASE_URI = 'mysql+oursql://root:mysql@localhost/outreach'

# Debug from SQLAlchemy
# Turn this to False on production
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

# List of allowed origins for CORS
ALLOWED_ORIGINS = "['*']"

# List of allowed IPs
WHITELIST_IPS = ["127.0.0.1"]

# Configure your log paths
LOG_FILE_DIRECTORY = 'logs'
LOG_FILE = 'outreach.log'

# Log level for the application
#10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL",
LOG_LEVEL = 10

# destination for uploaded files
# example value - '/static/uploads/'
UPLOAD_DIR_PATH = '/static/uploads/'

# allowed file extensions that can be uploaded
ALLOWED_FILE_EXTENSIONS = ['txt', 'TXT', 'pdf', 'PDF', 'png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG', 'gif', 'GIF', 'csv' , 'CSV', 'doc' , 'DOC', 'docx', 'DOCX']

# APP_URL
ELASTIC_IP = "http://10.100.2.40:9200"
#APP_URL = "http://localhost"
APP_URL = "http://outreach.virtual-labs.ac.in"

# Persona Verifier URL
PERSONA_VERIFIER_URL = "https://verifier.login.persona.org/verify"

#Google Authentication Credentials
CONSUMER_KEY = "420719460133-g13g6abnnised3v4nq4d430jo8mpb9m8.apps.googleusercontent.com"
CONSUMER_SECRET = "DQxOnwOectvfFFe05jqKTIQT"
