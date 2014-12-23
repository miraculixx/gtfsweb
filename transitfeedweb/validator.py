import os
import tempfile
import uuid

from transitfeedweb.download import download

from .feedvalidator import RunValidationOutputToFile


class DictObj(object):
    def __init__(self, d):
        self._data = d
    def __getattr__(self, attr):
        return self._data.get(attr)

class GTFSValidator(object):
    def __init__(self, url): 
        self.url = url
        self.feedfile = None
    
    def download(self):
        assert self.urlExists(self.url)
        tempfile = os.path.join('/tmp', '%s.zip' % str(uuid.uuid4()))
        self.feedfile = download(self.url, out=tempfile)
        return self.feedfile
    
    def validate(self, feed, options=None):
        options = options or self.defaultOptions()
        try:
            output_file = tempfile.NamedTemporaryFile('w+')
            RunValidationOutputToFile(feed, options, output_file)
            output_file.seek(0)
            results = output_file.readlines()
            output_file.close()
        except IOError, e:
            raise
        results = ' '.join(results) if isinstance(results, list) else results
        return results.decode('utf-8', 'ignore')
    
    def cleanup(self):
        if self.feedfile:
            os.remove(self.feedfile)
    
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
        import urllib2
        ret = urllib2.urlopen(url)
        return ret.code == 200
        

             
