import os
import traceback

from flask import Flask
from flask.globals import request
from flask.helpers import url_for, send_from_directory
from flask.templating import render_template
from flask_basicauth import BasicAuth
from werkzeug.utils import secure_filename, redirect

from transitfeedweb.validator import GTFSValidator


app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = os.environ.get('GTFSWEB_USERNAME', 'user')
app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('GTFSWEB_PASSWORD', 'useruser')
app.config['UPLOAD_FOLDER'] = os.environ.get('GTFSWEB_UPLOADFOLDER', '/tmp')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

basic_auth = BasicAuth(app)

@app.route('/')
@basic_auth.required
def index():
    feedurl = request.args.get('feedurl')
    results = None
    error = None
    if feedurl:
        validator = GTFSValidator()
        feed, error = validator.get_feed_file(feedurl, 
                                              app.config['UPLOAD_FOLDER'],
                                              'upload:')
        
        if not error:
            results = validator.validate(feed)
        validator.cleanup(feed) 
    return render_template('index.html', feedurl=feedurl or '', results=results, error=error)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and '.zip' in file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('/?feedurl=upload:/%s' % filename)
    return redirect('/')
    

if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 5000))
