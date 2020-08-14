from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ksAxqSFkkZ9AUzpoQCwcaAeJH0Jkt076'
app.config['SQLITE_DB_URI'] = 'sqlite:///freshPicks.sqlite'