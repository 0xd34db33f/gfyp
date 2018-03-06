#!/usr/bin/python
"""A utility for maintaining the GFYP database."""

import sys
import csv
import logging
import shutil
from datetime import datetime

import gfyp_db #gfyp_db.py
from common import pretty_print, log #common.py

def usage():
    """Print usage info."""
    usage_str = (
        "GFYP Utilities\n"
        "usage: python util.py <$BOLD$command$END$> [command parameters space "
        "separated]\n"
        "Commands:\n"
        "    $BOLD$usage$END$ - prints this message\n"
        "    $BOLD$build$END$ - creates a blank database named db.db\n"
        "    $BOLD$add$END$ (domain name) (email address) [optional: filename of csv file containing additional tlds] - inserts a new "
        "domain(s) to monitor into db.db\n"
        "    $BOLD$removemonitor$END$ (domain name) - removes a domain from "
        "being monitored\n"
        "    $BOLD$removeentry$END$ (domain name) - removes an identified "
        "domain from the found entries\n"
        "    $BOLD$dump$END$ (file name) - Writes the contents of the found "
        "domain name table into the file in CSV format\n"
        "    $BOLD$migrate$END$ - Upgrades the GFYP database to the most "
        "recent schema format\n"
        "    $BOLD$addnote$END$ (domain name) (note in quotes)- Add a note "
        "to a discovered domain entry")
    pretty_print(usage_str)
    sys.exit()

def dump():
    """Write database to CSV file."""
    filename = sys.argv[2]
    with gfyp_db.DatabaseConnection() as db_con:
        with open(filename, 'wb') as csvfile:
            csvoutput = csv.writer(csvfile)
            found_entries = db_con.get_all_found_domains()
            entries_iter = found_entries.fetchall()
            for entry in entries_iter:
                csvoutput.writerow(entry)
    print(("Wrote %d entries to '%s'." % (len(entries_iter), filename)))

def build():
    """Create tables."""
    with gfyp_db.DatabaseConnection() as db_con:
        is_err = db_con.table_init()
        err_msg = ", but with errors"
        msg = "Database is initalized%s." % (err_msg if is_err else '')
        print(msg)
        log_level = logging.ERROR if is_err else logging.INFO
        log(msg, log_level)

def add_domain():
    """Inserts a new domain to monitor"""
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        log("Incorrect number of arguments for adding domain: %s" % sys.argv,
            logging.ERROR)
        usage()
    email_notif_addr = sys.argv[3]
    domain_list = []
    domain_list.append(sys.argv[2])
    if len(sys.argv) == 5:
        #Looks like a TLD file is present, add them as well
        baseName = ((sys.argv[2]).rsplit('.'))[0]
        with open(sys.argv[4],'rb') as csvfile:
            csvreader = csv.reader(csvfile)
            for tld in csvreader:
                domain_list.append(baseName+"."+tld[0])
    with gfyp_db.DatabaseConnection() as db_con:
        for domain in domain_list:
            db_con.add_watch_entry(domain, email_notif_addr)

def remove_domain():
    """Removes a domain from being monitored"""
    domain_name = sys.argv[2]
    with gfyp_db.DatabaseConnection() as db_con:
        db_con.delete_watch_entry(domain_name)

def remove_entry():
    """Removes an identified domain from the list of found entries"""
    domain_name = sys.argv[2]

    with gfyp_db.DatabaseConnection() as db_con:
        db_con.delete_found_domain(domain_name)

def migrate():
    """Update the database to the current schema version"""
    is_curr = False
    db_ver = 0

    with gfyp_db.DatabaseConnection() as db_con:
        is_curr = db_con.is_db_current()
        db_ver = db_con.get_version()

    if not is_curr:
        dst = "db.bak.%s" % str(datetime.now())
        msg = "Updated database to most recent version - Existing database stored as: %s" % dst
        shutil.move("db.db",dst)
        build()
        if db_ver == 0:
            # Case db_ver == 0: Needs to be modified to account for UNIQUE monitor domains
            with gfyp_db.DatabaseConnection() as db_con:
                with gfyp_db.DatabaseConnection(filename=dst) as old_db_con:
                    existing_watch_entries = old_db_con.get_watch_entries()
                    for entry in existing_watch_entries:
                        db_con.add_watch_entry(entry[1],entry[0])

                    existing_found_entries = old_db_con.get_all_found_domains()
                    entries_iter = existing_found_entries.fetchall()
                    for entry in entries_iter:
                        db_con.add_discovered_domain(entry[0],entry[1])
    else:
        msg = "Database is currently at the most recent schema version. No changes necessary."

    print(msg)
    log(msg,logging.INFO)

def addnote():
    """Add a note for a found domain"""
    domain_name = sys.argv[2]
    note = sys.argv[3]
    with gfyp_db.DatabaseConnection() as db_con:
        db_con.add_note(domain_name,note)

FUNCTIONS = {'build': build,
             'usage': usage,
             'add': add_domain,
             'removeentry' : remove_entry,
             'removemonitor' : remove_domain,
             'dump' : dump,
             'migrate' : migrate,
             'addnote' : addnote}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in FUNCTIONS:
        log("Invalid arguments: %s" % sys.argv, logging.ERROR)
        usage()
    else:
        # python util.py (utility function argument) (function parameters space separated)
        FUNCTIONS[sys.argv[1]]()
