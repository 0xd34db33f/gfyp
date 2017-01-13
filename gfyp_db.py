"""Functions for interacting with the database."""
import sqlite3

DB_FILENAME_DEFAULT = 'db.db'

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

    def table_init(self):
        """Initialize database with required tables.

        Return: bool: Whether any errors were encounterd.
        """
        is_err = False
        try:
            self.sql_execute(
                "CREATE TABLE lookupTable(emailAddy text, domainName text)")
        except sqlite3.OperationalError, err:
            print "Error creating table: %s" % str(err)
            is_err = True

        try:
            self.sql_execute(
                "CREATE TABLE foundDomains(domainName text, info text)")
        except sqlite3.OperationalError, err:
            print "Error creating table: %s" % str(err)
            is_err = True
        return is_err

    def add_watch_entry(self, domain_name, alert_email):
        """Add a domain to monitor for phishing variants."""
        stmt = "INSERT INTO lookupTable VALUES (?, ?)"
        arglist = (alert_email, domain_name)
        num_changes = self.sql_execute(stmt, arglist)
        if num_changes == 1:
            print "Added domain %s for monitoring." % domain_name
        elif num_changes == 0:
            print "No domains added for monitoring! Already present?"
        else:
            print "Made more database changes (%d) than expected!" % num_changes

    def delete_watch_entry(self, domain_name):
        """Delete all entries for monitoring for specified domain."""
        stmt = "DELETE FROM lookupTable WHERE lookupTable.domainName = ?"
        arglist = (domain_name,)
        num_changes = self.sql_execute(stmt, arglist)
        if num_changes == 0:
            print "No domains removed from monitoring! Not already present?"
        else:
            print("Removed %s from monitoring and removed %d alert%s." %
                  (domain_name, num_changes, 's' if num_changes != 1 else ''))

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
        if num_changes == 0:
            print "No domains removed from list! Not previously found?"
        elif num_changes == 1:
            print("Removed domain %s from list of previously discovered domains." %
                  domain_name)
        else:
            print "Made more database changes (%d) than expected!" % num_changes

    def get_matching_found_domains(self, domain_name):
        """Get list of (domain, info) previously found matching specified domain.

        Returns: List of tuples (domain, info) of length >= 0
        """
        cur = self.conn.cursor()
        stmt = "SELECT * FROM foundDomains WHERE domainName = ?"
        arglist = (domain_name,)
        info_entries = cur.execute(stmt, arglist)
        return info_entries

    def add_discovered_domain(self, domain_name, domain_info):
        """Add a new domain to list of domains discovered by dnstwist.
        Args:
            domain_name (str): The name of the domain, e.g. 'example.com'.
            domain_info (str): Additiona DNS information from DNS lookup.
        """
        cur = self.conn.cursor()
        stmt = "INSERT INTO foundDomains VALUES (?, ?)"
        arglist = (domain_name, domain_info)
        cur.execute(stmt, arglist)
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
