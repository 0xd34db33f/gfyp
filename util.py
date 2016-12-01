#!/usr/bin/python

import sqlite3
import sys
import csv

def usage():
    print("GFYP Utilities\n"
          "python utils.py (utility function argument) (function parameters "
          "space separated)\n"
          "Current supported utility functions:\n"
          "usage - prints this message\n"
          "build - creates a blank database named db.db\n"
          "add (domain name) (email address) - inserts a new domain to monitor "
          "into db.db\n"
          "removemonitor (domain name) - removes a domain from being monitored\n"
          "removeentry (domain name) - removes an identified domain from the "
          "found entries\n"
          "dump (file name) - Writes the contents of the found domain name "
          "table into the file in CSV format")

def dump():
    with open(sys.argv[2],'wb') as csvfile:
        csvoutput = csv.writer(csvfile)
        conn = sqlite3.connect('db.db')
        c = conn.cursor()
        foundEntries = c.execute("SELECT * FROM foundDomains")
        entriesIter = foundEntries.fetchall()
        for entryItem in entriesIter:
            csvoutput.writerow(entryItem)
        conn.close()

def sql_execute(stmt, arglist=None):
    """Execute the SQL statement."""
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    if arglist is not None:
        c.execute(stmt, arglist)
    else:
        c.execute(stmt)
    conn.commit()
    conn.close()

def build():
    """Create tables."""
    sql_execute("CREATE TABLE lookupTable(emailAddy text,domainName text)")
    sql_execute("CREATE TABLE foundDomains(domainName text, info text)")

def addDomain():
    stmt = "INSERT INTO lookupTable VALUES (?, ?)"
    arglist = (sys.argv[3],sys.argv[2])
    sql_execute(stmt, arglist)

def removeDomain():
    stmt = "DELETE FROM lookupTable WHERE lookupTable.domainName = ?"
    arglist = (sys.argv[2])
    sql_execute(stmt, arglist)

def removeEntry():
    stmt = "DELETE FROM foundDomains WHERE foundDomains.domainName = ?"
    arglist = sys.argv[2]
    sql_execute(stmt, arglist)

functions = {'build': build,
             'usage': usage,
             'add': addDomain,
             'removeentry' : removeEntry,
             'removemonitor' : removeDomain,
             'dump' : dump}

if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1] in functions:
        usage()
    else:
        # python util.py (utility function argument) (function parameters space separated)
        functions[sys.argv[1]]()
