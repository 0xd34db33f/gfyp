GFYP - Go "Find Your" Phishers
========
Having experimented with dnstwist for some time now, it dawned on me that it could be useful for alerting of new domains as they pop up related to your domains of interest. 

For more information on dnstwist, see https://github.com/elceef/dnstwist

Installation
----------------
pip install -r requirements.txt
Add notification email information (username/password) to the top of core.py
python util.py build
python util.py add (domain name) (email address)

Then just python core.py (or set it as a cron job) to start getting information reports hourly.

Notes
---------------

Yes I know some of the coding is horrible. I'm going to be cleaning it up sometime in the next few weeks here when I get some time, just wanting to share it for now.
