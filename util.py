#!/usr/bin/python

import sqlite3
import sys

def usage():
	print "GFYP Utilities"
	print "python utils.py (utility function argument) (function parameters space separated)"
	print "Current supported utility functions:"
	print "usage - prints this message"
	print "build - creates a blank database named db.db"
	print "insert (domain name) (email address) - inserts a new domain to monitor into db.db"
	print "remove (domain name) - removes a domain from being monitored"
	print "removeentry (domain name) - removes an identified domain from the found entries"

def build():
        conn = sqlite3.connect('db.db')
        c = conn.cursor()
        c.execute("CREATE TABLE lookupTable(emailAddy text,domainName text)")
        c.execute("CREATE TABLE foundDomains(domainName text, info text)")
        conn.commit()
        conn.close()

def addDomain():
        conn = sqlite3.connect('db.db')
        c = conn.cursor()
        c.execute("INSERT INTO lookupTable VALUES (\"%s\",\"%s\")" % (sys.argv[3],sys.argv[2]))
        conn.commit()
        conn.close()

def removeDomain():
	conn = sqlite3.connect('db.db')
        c = conn.cursor()
        c.execute("DELETE FROM lookupTable WHERE lookupTable.domainName = \"%s\"" % (sys.argv[2]))
        conn.commit()
        conn.close()

def removeEntry():
        conn = sqlite3.connect('db.db')
        c = conn.cursor()
        c.execute("DELETE FROM foundDomains WHERE foundDomains.domainName = \"%s\"" % (sys.argv[2]))
        conn.commit()
        conn.close()

functions = {
		'build': build,
     		'usage': usage,
		'add': addDomain,
		'removeentry' : removeEntry,
		'remove' : removeDomain
	}

if __name__ == "__main__":
	if len(sys.argv) < 2:
		usage()
	else:
    		# python util.py (utility function argument) (function parameters space separated)
    		functions[sys.argv[1]]()
