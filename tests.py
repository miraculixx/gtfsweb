'''
Created on Dec 22, 2014

@author: patrick
'''
import os
import unittest

from transitfeedweb.validator import GTFSValidator


class Test(unittest.TestCase):
    GTFS_FEED = 'https://developers.google.com/transit/gtfs/examples/sample-feed.zip'

    def testValidator(self):
        validator = GTFSValidator(self.GTFS_FEED)
        feed = validator.download()
        result = validator.validate(feed)
        self.assertTrue('html' in result)
        validator.cleanup()
        self.assertFalse(os.path.exists(feed))


if __name__ == "__main__":
    unittest.main()