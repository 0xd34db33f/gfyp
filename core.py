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

EMAIL_USERNAME = "EMAIL_ADDRESS_GOES_HERE"
EMAIL_PASSWORD = "EMAIL_PASSWORD_GOES_HERE"
EMAIL_STMPSERVER = "SMTP_SERVER_GOES_HERE"
def send_email(recipient, subject, body):

	FROM = EMAIL_USERNAME
	TO = [recipient]
	SUBJECT = subject
	TEXT = body

	#Sending message, first construct actual message
	message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
	""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
	try:
		server_ssl = smtplib.SMTP_SSL(EMAIL_STMPSERVER, 465)
		server_ssl.ehlo()
		server_ssl.login(EMAIL_USERNAME, EMAIL_PASSWORD)  
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
			send_email(row[0],'GFYP - New Entries for %s' % row[1],body) 
	conn.commit()
	conn.close()

if __name__ == "__main__":
    main()
