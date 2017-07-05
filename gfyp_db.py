"""Functions for interacting with the database."""
import sqlite3
import logging
from common import log #common.py

DB_FILENAME_DEFAULT = 'db.db'
DB_SCHEMA_VERSION = 1

class DatabaseConnection(object):
    """A connection to the database.

    Usage:
        with gfyp_db.DatabaseConnection() as db_con:
            db_con.foo()
            ...
    """

    def __init__(self, filename=DB_FILENAME_DEFAULT):
        self.filename = filename
        self.conn = sqlite3.connect(self.filename)

    def __enter__(self):
        return self

    def __exit__(self, exec_type, exec_value, exec_traceback):
        self.conn.close()

    def _create_table(self, stmt):
        try:
            self.sql_execute(stmt)
        except sqlite3.OperationalError as err:
            msg = "Error creating table: %s" % str(err)
            print(msg)
            log(msg, logging.ERROR)
            return True
        return False

    def table_init(self):
        """Initialize database with required tables.

        Return: bool: Whether any errors were encounterd.
        """
        stmt1 = "CREATE TABLE lookupTable(emailAddy text, domainName text UNIQUE)"
        stmt2 = "CREATE TABLE foundDomains(domainName text, info text, notes text,dateFound integer)"
        stmt3 = "PRAGMA user_version = %s" % str(DB_SCHEMA_VERSION)
        return self._create_table(stmt1) or self._create_table(stmt2) or self._create_table(stmt3)

    def add_watch_entry(self, domain_name, alert_email):
        """Add a domain to monitor for phishing variants."""
        stmt = "INSERT INTO lookupTable VALUES (?, ?)"
        arglist = (alert_email, domain_name)
        try:
            num_changes = self.sql_execute(stmt, arglist)
            msg = ""
            log_level = logging.INFO
            msg = "Added domain %s for monitoring." % domain_name
        except sqlite3.IntegrityError:
            msg = "No domains added for monitoring! Already present? - %s" % domain_name
            log_level = logging.WARNING

        print(msg)
        log(msg, log_level)

    def delete_watch_entry(self, domain_name):
        """Delete all entries for monitoring for specified domain."""
        stmt = "DELETE FROM lookupTable WHERE lookupTable.domainName = ?"
        arglist = (domain_name,)
        num_changes = self.sql_execute(stmt, arglist)
        msg = ""
        log_level = logging.INFO
        if num_changes == 0:
            msg = "No domains removed from monitoring! Not already present?"
            log_level = logging.WARNING
        else:
            msg = ("Removed %s from monitoring and removed %d alert%s." %
                   (domain_name, num_changes, 's' if num_changes != 1 else ''))
        print(msg)
        log(msg, log_level)

    def get_watch_entries(self):
        """Get a list of (email, domain) entries monitored for phishing variants.

        Returns: List of tuples (alert_email, domain) of length >= 0
        """
        cur = self.conn.cursor()
        domain_entries = cur.execute('SELECT * FROM lookupTable').fetchall()
        return domain_entries

    def get_all_found_domains(self):
        """Get list of (domain, info) previously found.

        Returns: List of tuples (domain, info) of length >= 0
        """
        cur = self.conn.cursor()
        info_entries = cur.execute("SELECT * FROM foundDomains")
        return info_entries

    def delete_found_domain(self, domain_name):
        """Delete all entries from list of domains found that match domain."""
        stmt = "DELETE FROM foundDomains WHERE foundDomains.domainName = ?"
        arglist = (domain_name,)
        num_changes = self.sql_execute(stmt, arglist)
        msg = ""
        log_level = logging.INFO
        if num_changes == 0:
            msg = "No domains removed from list! Not previously found?"
            log_level = logging.WARNING
        elif num_changes == 1:
            msg = ("Removed domain %s from list of previously discovered domains." %
                   domain_name)
        else:
            msg = "Made more database changes (%d) than expected!" % num_changes
            log_level = logging.ERROR

        print(msg)
        log(msg, log_level)

    def get_matching_found_domains(self, domain_name):
        """Get list of (domain, info) previously found matching specified domain.

        Returns: List of tuples (domain, info) of length >= 0
        """
        cur = self.conn.cursor()
        stmt = "SELECT * FROM foundDomains WHERE domainName = ?"
        arglist = (domain_name,)
        info_entries = cur.execute(stmt, arglist)
        return info_entries

    def get_found_domains_last_seven_days(self):
        """Get list of found domain entries from last seven days"""
        cur = self.conn.cursor()
        stmt = "SELECT * from foundDomains where strftime('%s','now') - dateFound < 604800"
        info_entries = cur.execute(stmt)
        return info_entries

    def add_discovered_domain(self, domain_name, domain_info):
        """Add a new domain to list of domains discovered by dnstwist.
        Args:
            domain_name (str): The name of the domain, e.g. 'example.com'.
            domain_info (str): Additiona DNS information from DNS lookup.
        """
        cur = self.conn.cursor()
        stmt = "INSERT INTO foundDomains VALUES (?, ?, ?, strftime('%s','now'))"
        arglist = (domain_name, domain_info,"")
        cur.execute(stmt, arglist)
        self.conn.commit()

    def is_db_current(self):
        """Gets the user_version from the db and checks to see if it matches the current schema number"""
        cur = self.conn.cursor()
        stmt = "PRAGMA user_version"
        info = cur.execute(stmt)
        return DB_SCHEMA_VERSION == (info.fetchone())[0]

    def get_version(self):
        """Gets the user_version from the db and returns the value"""
        cur = self.conn.cursor()
        stmt = "PRAGMA user_version"
        info = cur.execute(stmt)
        return (info.fetchone())[0]

    def add_note(self,domain_name, note):
        """Adds a note to a discovered domain"""
        cur = self.conn.cursor()
        stmt = "UPDATE foundDomains SET notes = ? WHERE domainName = ?"
        arglist = (note,domain_name)
        cur.execute(stmt,arglist)
        self.conn.commit()

    def sql_execute(self, stmt, arglist=None):
        """Execute the SQL statement and return number of db changes."""
        cur = self.conn.cursor()
        if arglist is not None:
            cur.execute(stmt, arglist)
        else:
            cur.execute(stmt)
        self.conn.commit()
        num_changes = self.conn.total_changes
        return num_changes
