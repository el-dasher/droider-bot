from pyrebase import pyrebase
import json
from src.paths import FIREBASE_CONFIG_PATH


firebase_config = json.loads((str(json.load(open(FIREBASE_CONFIG_PATH))).replace("'", '"')))
firebase = pyrebase.initialize_app(firebase_config)

database = firebase.database()
