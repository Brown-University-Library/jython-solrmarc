"""
Scans III MARC record exports and finds records updated within a
particular time period.

Command line options:
-f file
-d days - number of days to go back and look for updates
-s start - start date for updates
-e end - end dates for updates
"""

import logging
import os
import optparse
import sys
import urllib2

from datetime import datetime, timedelta, date

from java.lang import RuntimeException
from java.io import InputStream
from java.io import File, FileInputStream, ByteArrayOutputStream, FileOutputStream

from org.marc4j import MarcStreamReader, MarcPermissiveStreamReader, MarcStreamWriter
from org.marc4j import ErrorHandler

from org.solrmarc.tools import MarcUtils
from com.solrmarc.icu.text import Normalizer


def read_file(infile):
    inpath, inname = os.path.split(infile)
    f = FileInputStream(infile)
    #lifted from https://github.com/billdueber/marc_marc4j/blob/master/lib/marc/marc4j/reader.rb
    reader = MarcPermissiveStreamReader(f, True, False, "BESTGUESS")
    return reader

def convert_date(datestr):
    """III Only reports two digit year numbers."""
    dgroups = datestr.split('-')
    try:
        month = int(dgroups[0])
        day = int(dgroups[1])
        year = int(dgroups[2])
    except ValueError, e:
        return
    this_year = (date.today().year) - 2000
    #If the year integer is greater than the current year then,
    #pad with 1900.
    if year > this_year:
        year = 1900 + year
    else:
        year = 2000 + year
    try:
        return date(year, month, day) #.isoformat() + 'Z'
    except ValueError:
        return


def delete_docs(rec_ids, solr_url):
    id_string = ''.join(['<id>%s</id>' % i for i in rec_ids])
    data = '<delete>%s</delete>' % id_string
    r = urllib2.Request(solr_url + 'update')
    r.add_header('Content-Type', 'text/xml')
    r.add_data(data)
    f = urllib2.urlopen(r)
    logging.info("Solr response to deletion request for records.\n" + f.read())

def main(mfile=None, days=1, **kwargs):
    #Are we doing a number of days check?
    days_check = True
    submit_size = 10

    solr_url = kwargs.get('solr_url')
    if solr_url is None:
        raise Exception("No SOLR URL passed in.")

    start = kwargs.get('start')
    end = kwargs.get('end')
    if start and end:
        days_check = False
        start = convert_date(start)
        end = convert_date(end)
        print>>sys.stderr, "Scanning records for updates between and including %s and %s." % (start, end)
    else:
        #do the days
        today = date.today()
        cutoff = today - timedelta(days=days)
        print>>sys.stderr, "Scanning for suppressed records since %s." % cutoff

    reader = read_file(mfile)

    to_remove = []

    while reader.hasNext():
        record = reader.next()
        #Get record id for logging.
        raw = record.getVariableField("907")
        rid = raw.getSubfield('a').getData()[1:9]
        raw_998 = record.getVariableField("998")
        value_998_e = raw_998.getSubfield('e').getData()
        #Continue if record isn't suppressed.
        if value_998_e != 'n':
            continue
        last_update_value = MarcUtils.getFieldList(record, "907b").toArray()[0]
        logging.debug("Last update for %s is %s." % (rid, last_update_value))
        last_update = convert_date(last_update_value)
        if last_update is None:
            logging.warning("No last update found for %s with %s." % (rid, last_update_value))
        if days_check:
            if last_update >= cutoff:
                to_remove.append(rid)
        else:
            if (last_update >= start) and (last_update <= end):
                to_remove.append(rid)

        size = len(to_remove)
        if (size > 0) and (size % submit_size == 0):
            logging.info("Removing %s.".join(','))
            delete_docs(to_remove, solr_url)
            to_remove = []

    if len(to_remove) != 0:
        logging.info("Removing %s.".join(','))
        delete_docs(to_remove, solr_url)

if __name__ == "__main__":
    p = optparse.OptionParser()
    p.add_option('--file', '-f',
               help="Pass in the file name.")
    p.add_option('--days',
               '-d',
               default=1,
               help='Pass in the number of days of updatees to\
                     pull from the catalog.',
    )
    p.add_option('--start',
               '-s',
               default=None,
               help='e.g. 02-01-10. Pass in the start date.'
    )
    p.add_option('--end',
               '-e',
               default=None,
               help='e.g. 02-01-10. Pass in the end date.'
    )
    p.add_option('--solr',
               '-u',
               default=None,
               help='Solr URL'
    )
    options, arguments = p.parse_args()
    mfile = os.path.realpath(options.file)
    days = int(options.days)
    logging.basicConfig(level=logging.INFO)
    main(mfile=mfile,
       days=days,
       start=options.start,
       end=options.end,
       solr_url=options.solr)
