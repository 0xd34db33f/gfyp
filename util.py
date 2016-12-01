#!/usr/bin/python
"""A utility for maintaining the GFYP database."""

import sqlite3
import sys
import csv

def usage():
    """Print usage info."""
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
    """Write database to CSV file."""
    with open(sys.argv[2], 'wb') as csvfile:
        csvoutput = csv.writer(csvfile)
        conn = sqlite3.connect('db.db')
        cur = conn.cursor()
        found_entries = cur.execute("SELECT * FROM foundDomains")
        entries_iter = found_entries.fetchall()
        for entry in entries_iter:
            csvoutput.writerow(entry)
        conn.close()

def sql_execute(stmt, arglist=None):
    """Execute the SQL statement."""
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    if arglist is not None:
        cur.execute(stmt, arglist)
    else:
        cur.execute(stmt)
    conn.commit()
    conn.close()

def build():
    """Create tables."""
    sql_execute("CREATE TABLE lookupTable(emailAddy text,domainName text)")
    sql_execute("CREATE TABLE foundDomains(domainName text, info text)")

def add_domain():
    """Inserts a new domain to monitor"""
    stmt = "INSERT INTO lookupTable VALUES (?, ?)"
    arglist = (sys.argv[3], sys.argv[2])
    sql_execute(stmt, arglist)

def remove_domain():
    """Removes a domain from being monitored"""
    stmt = "DELETE FROM lookupTable WHERE lookupTable.domainName = ?"
    arglist = (sys.argv[2])
    sql_execute(stmt, arglist)

def remove_entry():
    """Removes an identified domain from the list of found entries"""
    stmt = "DELETE FROM foundDomains WHERE foundDomains.domainName = ?"
    arglist = sys.argv[2]
    sql_execute(stmt, arglist)

FUNCTIONS = {'build': build,
             'usage': usage,
             'add': add_domain,
             'removeentry' : remove_entry,
             'removemonitor' : remove_domain,
             'dump' : dump}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in FUNCTIONS:
        usage()
    else:
        # python util.py (utility function argument) (function parameters space separated)
        FUNCTIONS[sys.argv[1]]()
