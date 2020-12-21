import json
from os import getenv

from github import Github
from pyrebase import pyrebase

FIREBASE_CONFIG = json.loads(Github(
        getenv("ACCESS_TOKEN")
).get_gist("37bbbbce6b64b2f4a5d3195d7d06df92").files["firebase_config.json"].content)

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
database = firebase.database()
