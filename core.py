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

import sqlite3
import sys
from dnslib import dnslib
import smtplib

EMAIL_USERNAME = INSERT_EMAIL_USERNAME_HERE
EMAIL_PASSWORD = INSERT_EMAIL_PASSWORD_HERE

def send_email(user, pwd, recipient, subject, body):

	gmail_user = user
	gmail_pwd = pwd
	FROM = user
	TO = [recipient]
	SUBJECT = subject
	TEXT = body

	# Prepare actual message
	message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
	""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
	try:
		server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
		server_ssl.ehlo() # optional, called by login()
		server_ssl.login(gmail_user, gmail_pwd)  
		server_ssl.sendmail(FROM, TO, message)
		server_ssl.close()
	except:
        	print "failed to send mail"

def main():
	dnsCheck = dnslib()
	conn = sqlite3.connect('db.db')
	c = conn.cursor()
	domainentries =  c.execute('SELECT * FROM lookupTable').fetchall()
	for row in domainentries:
		print "Now checking %s - %s" % (row[0], row[1])
		body = ""
		entries = dnsCheck.checkDomain(row[1])
		for entry in entries:
			foundEntries = c.execute("SELECT * FROM foundDomains WHERE domainName = '%s'" % entry[0])
			entriesIter = foundEntries.fetchall()
			if len(entriesIter) == 0:
				c.execute("INSERT INTO foundDomains VALUES ('%s','%s')" % (entry[0],entry[1]))
				body = body+"\r\n\r\n%s - %s" % (entry[0],entry[1])
		if body != "":
			send_email(EMAIL_USERNAME,EMAIL_PASSWORD,row[0],'GFYP - New Entries for %s' % row[1],body) 
	conn.commit()
	conn.close()

if __name__ == "__main__":
    main()
