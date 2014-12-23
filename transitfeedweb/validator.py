import os
import sys
import tempfile
import uuid

from transitfeedweb.util import download, which
import importlib

class DictObj(object):
    """
    a simple dict wrapper to allow .dot attribute access
    """
    def __init__(self, d):
        self._data = d
    def __getattr__(self, attr):
        return self._data.get(attr)
    def update(self, other):
        self._data.update(other)
        return self

class GTFSValidator(object):
    """
    A simple wrapper/proxy to Google's feedvalidator. It can
    process HTTP(s)-served feed URLs or local files. 
    
    Use:
       validator = GTFSValidator()
       file = validator.download(<some url>)  # optional
       results = validator.validate(file)     # pass full path
       => results is the HTML code as issued by feedvalidator
    """
    def __init__(self): 
        self.feedfile = None
        self.load_feedvalidator()
        
    def load_feedvalidator(self):
        """
        load Google's feed validator dynamically. It is installed
        in the virtualenv's /bin directory which is not directly
        added to PYTHONPATH. Let's do that.
        """
        feedvalidator = which('feedvalidator.py')
        if feedvalidator:
            sys.path.insert(0, os.path.dirname(feedvalidator))
            feedvalidator = importlib.import_module('feedvalidator')
            self.RunValidationOutputToFile = \
            feedvalidator.RunValidationOutputToFile
            return True
        return False 
    
    def download(self, url):
        """
        download a file using util.download and return the full path
        to the downloaded file. This generates a temporary file name first
        and makes sures it has a .zip ending, as feedvalidator won't accept
        anything else.
        """
        assert self.urlExists(url)
        tempfile = os.path.join('/tmp', '%s.zip' % str(uuid.uuid4()))
        self.feedfile = download(url, out=tempfile)
        return self.feedfile
    
    def validate(self, feed, **options):
        """
        validate the feed. This is the same as calling feedvalidator.py
        from the command line. feed is the full path + filename.zip of
        the file to be validated. It returns the HTML result as a string.
        """
        options = self.defaultOptions().update(options)
        try:
            output_file = tempfile.NamedTemporaryFile('w+')
            self.RunValidationOutputToFile(feed, options, output_file)
            output_file.seek(0)
            results = output_file.readlines()
            output_file.close()
        except IOError, e:
            raise
        except:
            # something may have gone wrong with loading the feed validator
            raise
        results = ' '.join(results) if isinstance(results, list) else results
        # avoid unicode related failures
        return results.decode('utf-8', 'ignore')
    
    def cleanup(self, feedfile):
        """
        delete the feedfile. If the validator has previously
        downloaded a file it will be deleted as well. 
        """
        for filename in [feedfile, self.feedfile]:
            if filename and os.path.exists(filename):
                os.remove(filename)
    
    def defaultOptions(self):
        options = {
            'check_duplicate_trips': False,
            'manual_entry': True,
            'extension': None,
            'error_types_ignore_list': None,
            'memory_db': False,
            'service_gap_interval': 13,
            'latest_version': '',
            'limit_per_type': 5,
            'performance': None,
            'output': 'validation-results.html',
        }
        return DictObj(options)
    
    def urlExists(self, url):
        """
        tries to access an URL and returns True if possible. 
        """
        import urllib2
        # FIXME ensure this does not download, just check. Should
        # really be a HEAD request? 
        ret = urllib2.urlopen(url)
        return ret.code == 200
    
    def get_feed_file(self, feedurl, local_folder=None, local_prefix='upload:'):
        """
        either download the file as given in feedurl or return a full path
        according to the local_folder and local_prefix. This is a convenience
        function so that we can keep the app code clean from transforming 
        URLs entered by the user. Accepts two types of input:
        
        1) actual feed URLs, http(s)://example.com/somefeed.zip
        2) local URI in the format upload:/path/to/file
        
        Given the first form, it will call self.download to download the
        file and then return the filename and/or error message.
        
        Given the second form, it will convert the local URI into a full
        path using the local_folder (by replacing the local_prefix in the
        URI with the local_folder). It also checks for existence of the
        file and returns an error message if it does not.
        """
        feed = None
        error = None
        # download?
        if feedurl and 'http' in feedurl:
            try:
                feed = self.download(feedurl)
            except Exception as e:
                error = e  
                # print error, traceback.print_exc()
        # or local file:
        elif local_prefix in feedurl:
            feed = feedurl.replace(local_prefix, local_folder)
            print feed
            if not os.path.exists(feed):
                error = 'Error uploading file %s' % feedurl
        else:
            error = 'This URL does not exist.'
        return feed, error
        

             
