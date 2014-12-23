gtfsweb
=======

transitfeed's feedvalidator as a simple web application

This is a simple web app that allows users to specify a GTFS feed URL and run [Google's feedvaliator](https://github.com/google/transitfeed/wiki/FeedValidator). 
It was created out of the need to repeatedly run GTFS validations for someone else who didn't have Python installed on their machine... 

How to install
--------------

```
git clone git@github.com:miraculixx/gtfsweb.git
cd gtfsweb
pip install -r requirements.txt
# without foreman
python app.py
# with foreman
foreman start
``` 

To avoid unauthorized users from downloading arbitrary content to your server, set the following two environment variables:

```
export GTFSWEB_USERNAME=<username>
export GTFSWEB_PASSWORD=<password>
```

Sample
------

![](docs/screenshot.png?raw=true)

Limitations
-----------

* feed is downloaded and validated within the same web request - no async processing. Large feeds will crash the server or timeout
* the download is using the `wget` command -- if someone knows of a Python-only download that actually works (including cookies and session processing), please open a PR. Will be happy to integrate
* single-user authentication

License
-------

The transitfeedweb package is released under the MIT license. Note that for the
actual feed validation, it installs and uses the transitfeed package released
by Google Inc. under the Apache License. 