#!/usr/bin/python
"""A utility for maintaining the GFYP database."""

import sys
import csv
import logging
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
        "    $BOLD$add$END$ (domain name) (email address) - inserts a new "
        "domain to monitor into db.db\n"
        "    $BOLD$removemonitor$END$ (domain name) - removes a domain from "
        "being monitored\n"
        "    $BOLD$removeentry$END$ (domain name) - removes an identified "
        "domain from the found entries\n"
        "    $BOLD$dump$END$ (file name) - Writes the contents of the found "
        "domain name table into the file in CSV format")
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
    print("Wrote %d entries to '%s'." % (len(entries_iter), filename))

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
    """Inserts a new domain to monitor

    Todos:
        * Should not add another record if <domain, email> pair is already
            present. Can do this by checking in Python or SQL constraint.
    """
    if len(sys.argv) != 4:
        log("Incorrect number of arguments for adding domain: %s" % sys.argv,
            logging.ERROR)
        usage()
    domain_name = sys.argv[2]
    email_notif_addr = sys.argv[3]

    with gfyp_db.DatabaseConnection() as db_con:
        db_con.add_watch_entry(domain_name, email_notif_addr)

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

FUNCTIONS = {'build': build,
             'usage': usage,
             'add': add_domain,
             'removeentry' : remove_entry,
             'removemonitor' : remove_domain,
             'dump' : dump}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in FUNCTIONS:
        log("Invalid arguments: %s" % sys.argv, logging.ERROR)
        usage()
    else:
        # python util.py (utility function argument) (function parameters space separated)
        FUNCTIONS[sys.argv[1]]()
