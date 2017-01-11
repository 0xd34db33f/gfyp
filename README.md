# GFYP - Go Find Your Phishers

This tool augments [dnstwist](https://github.com/elceef/dnstwist) with a database that tracks identified phishing sites over times, and provides email alerts when new ones are discovered.

## Installation

    $ pip install -r requirements.txt

## Configuration

1. Initialize database with `python util.py build`
2. Either add your SMTP credentials by hard-coding them in core.py, or set the
following environment variables:
    * `GFYP_EMAIL_USERNAME`
    * `GFYP_EMAIL_PASSWORD`
    * `GFYP_EMAIL_SMTPSERVER`

Ex.

    $ export GFYP_EMAIL_USERNAME=alice@example.com
    $ export GFYP_EMAIL_PASSWORD=ilovemallory
    $ export GFYP_EMAIL_SMTPSERVER=smtp.example.com

## Usage

    # add domain to list for which to hunt phishing domains
    python util.py add (domain name) (email address)
    # start searching process
    python core.py # or set it as a cron job to regular reports

## Troubleshooting

### GMail

If using GMail as an SMTP provider, you may first need to log into GMail in the web interface and enable the "Allow less secure apps" option in the "Sign-in & security" section.
