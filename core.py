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

from dnslib import dnslib #dnslib.py
import gfyp_db #gfyp_db.py

#SET EMAIL SETTINGS HERE IF NOT USING ENVIRONMENT VARIABLES
EMAIL_USERNAME = None
EMAIL_PASSWORD = None
EMAIL_STMPSERVER = None

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
        #TODO: log me
        sys.exit("Failed to send mail: %s" % str(err))

    print "Email sent to %s." % recipient

def main():
    """Description: Search for new domain variants and email alerts for new ones.
    """
    #Get configuration from env variables or fallback to hard-coded values
    smtp_auth = dict()
    smtp_auth['username'] = os.getenv('GFYP_EMAIL_USERNAME', EMAIL_USERNAME)
    smtp_auth['password'] = os.getenv('GFYP_EMAIL_PASSWORD', EMAIL_PASSWORD)
    smtp_auth['server'] = os.getenv('GFYP_EMAIL_STMPSERVER', EMAIL_STMPSERVER)
    for key, value in smtp_auth.iteritems():
        if value is None:
            sys.exit("Fatal error: Email setting '%s' has not been set." % key)

    if any([EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_STMPSERVER]):
        print("WARNING: You have hard-coded credentials into a code file. Do "
              "not commit it to a public Git repo!")

    dns_check = dnslib()
    with gfyp_db.DatabaseConnection() as db_con:
        domain_entries = db_con.get_watch_entries()

        if len(domain_entries) == 0:
            print "No domains have been added for watching/alerts. Use util.py to add domains."

        for row in domain_entries:
            alert_email = row[0]
            domain = row[1]
            print "Now checking %s - %s" % (alert_email, domain)
            body = ""
            entries = dns_check.checkDomain(domain)
            print "DNSTwist found %d variant domains from %s." % (len(entries), domain)
            for domain_found, domain_info in entries:
                found_entries = db_con.get_matching_found_domains(domain_found)
                entries_iter = found_entries.fetchall()

                if len(entries_iter) == 0:
                    db_con.add_discovered_domain(domain_found, domain_info)
                    body += "\r\n\r\n%s - %s" % (domain_found, domain_info)

            if body != "":
                recipient = alert_email
                subject = 'GFYP - New Entries for %s' % domain
                send_email(smtp_auth, recipient, subject, body)

if __name__ == "__main__":
    main()
