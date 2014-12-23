import os
import traceback

from flask import Flask
from flask.globals import request
from flask.templating import render_template
from flask_basicauth import BasicAuth

from transitfeedweb.validator import GTFSValidator


app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'bbookers'
app.config['BASIC_AUTH_PASSWORD'] = 'Mascen19'

basic_auth = BasicAuth(app)

@app.route('/')
@basic_auth.required
def index():
    feedurl = request.args.get('feedurl')
    results = None
    error = None
    if feedurl:
        validator = GTFSValidator(feedurl)
        try:
            feed = validator.download()
        except Exception as e:
            error = e  
            print error, traceback.print_exc()
        else:
            results = validator.validate(feed)
        validator.cleanup()
    return render_template('index.html', feedurl=feedurl or '', results=results, error=error)

if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 5000))