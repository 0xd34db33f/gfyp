#!/usr/bin/python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Checks database for new phishing entries and executes alerts."""

import os
import sys
import smtplib
import logging

from dnslib import dnslib #dnslib.py
import gfyp_db #gfyp_db.py
from common import pretty_print, log #common.py

#SET EMAIL SETTINGS HERE IF NOT USING ENVIRONMENT VARIABLES
EMAIL_USERNAME = None
EMAIL_PASSWORD = None
EMAIL_SMTPSERVER = None

def send_email(smtp_auth, recipient, subject, body):
    """Send email via SMTP.
    Args:
        smtp_auth (dict): Contains 'username' (str), 'password' (str), and
            'server' (str).
        recipient (str): The email address to send to
        subject (str)
        body (str)

    http://stackoverflow.com/questions/10147455/trying-to-send-email-gmail-as-mail-provider-using-python
    """
    email_to = [recipient]

    #Sending message, first construct actual message
    message = ("From: %s\nTo: %s\nSubject: %s\n\n%s" %
               (smtp_auth['username'], ", ".join(email_to), subject, body))
    try:
        server_ssl = smtplib.SMTP_SSL(smtp_auth['server'], 465)
        server_ssl.ehlo()
        server_ssl.login(smtp_auth['username'], smtp_auth['password'])
        server_ssl.sendmail(smtp_auth['username'], email_to, message)
        server_ssl.close()
    except Exception, err:
        msg = "Failed to send mail: %s" % str(err)
        log(msg, logging.ERROR)
        sys.exit(msg)

    msg = "Email sent to %s." % recipient
    print msg
    log(msg)

def check_and_send_alert(smtp_auth, alert_email, domain, escape_alert=False,
                         db_con=None):
    """Consult DB whether an alert needs to be sent for domain, and send one.
    Args:
        smtp_auth (dict): Credentials for SMTP server, including 'username',
            'password', and 'server'.
        alert_email (str)
        domain (str)
        escape_alert (bool): Whether or not to escape periods in the email body
            in order to avoid spam filtering. (Default: False)
        db_con (None or `gfyp_db.DatabaseConnection`): This can optionally
            provide a database connection to reuse. Otherwise, a new one will
            be created.
    """
    msg = "Now checking %s - %s" % (alert_email, domain)
    print msg
    log(msg)
    close_db = False
    if db_con is None:
        db_con = gfyp_db.DatabaseConnection()
        close_db = True
    body = ""
    dns_check = dnslib()
    entries = dns_check.checkDomain(domain)
    msg = "DNSTwist found %d variant domains from %s." % (len(entries), domain)
    print msg
    log(msg)
    num_new_entries = 0
    for domain_found, domain_info in entries:
        found_entries = db_con.get_matching_found_domains(domain_found)
        entries_iter = found_entries.fetchall()

        if len(entries_iter) == 0:
            db_con.add_discovered_domain(domain_found, domain_info)
            body += "\r\n\r\n%s - %s" % (domain_found, domain_info)
            num_new_entries += 1

    if body != "":
        recipient = alert_email
        subject = 'GFYP - New Entries for %s' % domain
        if escape_alert:
            body = body.replace('.', '[.]')
        send_email(smtp_auth, recipient, subject, body)

    msg = "Found %d new domain variants from %s" % (num_new_entries, domain)
    print msg
    log(msg)

    if close_db:
        db_con.conn.close()

def main():
    """Description: Search for new domain variants and email alerts for new ones.
    """
    args = get_args()
    #Get configuration from env variables or fallback to hard-coded values
    smtp_auth = dict()
    smtp_auth['username'] = os.getenv('GFYP_EMAIL_USERNAME', EMAIL_USERNAME)
    smtp_auth['password'] = os.getenv('GFYP_EMAIL_PASSWORD', EMAIL_PASSWORD)
    smtp_auth['server'] = os.getenv('GFYP_EMAIL_SMTPSERVER', EMAIL_SMTPSERVER)
    for key, value in smtp_auth.iteritems():
        if value is None:
            msg = "Fatal error: Email setting '%s' has not been set." % key
            log(msg, logging.ERROR)
            sys.exit(msg)

    if any([EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_SMTPSERVER]):
        msg = ("WARNING: You have hard-coded credentials into a code file. Do "
               "not commit it to a public Git repo!")
        print(msg)
        log(msg, logging.WARNING)

    with gfyp_db.DatabaseConnection() as db_con:
        domain_entries = db_con.get_watch_entries()

        if len(domain_entries) == 0:
            msg = ("No domains have been added for watching/alerts. Use "
                   "util.py to add domains.")
            print msg
            log(msg)

        for row in domain_entries:
            alert_email = row[0]
            domain = row[1]
            check_and_send_alert(
                smtp_auth, alert_email, domain,
                escape_alert=args['escape_alert'], db_con=db_con)

def usage():
    """Print usage info."""
    usage_str = (
        "GFYP Core - Find domain variants and send alerts\n"
        "usage: python core.py [$BOLD$-escapealert$END$]\n"
        "Options:\n"
        "    $BOLD$-escapealert$END$ - Escape periods in email alert to avoid "
        "spam filter")
    pretty_print(usage_str)
    sys.exit()

def get_args():
    """Get command line arguments.

    Current arguments:
        * escape_alert (bool): Whether to escape periods in alert email.
    """
    args = dict()
    args['escape_alert'] = False
    if len(sys.argv) == 1:
        return args
    elif len(sys.argv) == 2:
        if sys.argv[1] == '-escapealert':
            args['escape_alert'] = True
        else:
            log("Invalid arguments: %s" % sys.argv, logging.ERROR)
            usage()
    else:
        log("Invalid arguments: %s" % sys.argv, logging.ERROR)
        usage()
    return args

if __name__ == "__main__":
    main()
