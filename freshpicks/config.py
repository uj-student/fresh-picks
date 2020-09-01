from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ksAxqSFkkZ9AUzpoQCwcaAeJH0Jkt076'
app.config['SQLITE_DB_URI'] = 'sqlite:///freshPicks.sqlite'
app.config['UPLOAD_FOLDER'] 	# Defines path for upload folder
app.config['MAX_CONTENT_PATH'] # Specifies maximum size of file yo be uploaded – in bytes

if __name__ == '__main__':
    app.run(debug=True)