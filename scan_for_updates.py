"""
Scans III MARC record exports and finds records updated within a
particular time period.  

Command line options: 
-f file
-d days - number of days to go back and look for updates
-o output - directory to store the MARC records.  
-s start - start date for updates
-e end - end dates for updates
"""

import logging 
import os
import optparse
import sys

from datetime import datetime, timedelta, date

from java.lang import RuntimeException
from java.io import InputStream
from java.io import File, FileInputStream, ByteArrayOutputStream, FileOutputStream

from org.marc4j import MarcStreamReader, MarcPermissiveStreamReader, MarcStreamWriter
from org.marc4j import ErrorHandler

from org.solrmarc.tools import MarcUtils
from com.solrmarc.icu.text import Normalizer

logging.basicConfig(level=logging.WARNING)

#Default local directory to store written MARC records.  Pass in -o to change.  
OUTPUT_DIR = 'to_load'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

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
 
def main(mfile=None, days=1, **kwargs):
    #Are we doing a number of days check?
    days_check = True

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
        print>>sys.stderr, "Scanning records for updates since %s." % cutoff

    reader = read_file(mfile)
    #get the filename from input path for output
    ofilename = mfile.split(os.path.sep)[-1]
    odir = OUTPUT_DIR if kwargs.get('output_dir') is None else kwargs.get('output_dir')
    out_file = File('%s/updates_%s' % (odir, ofilename))
    #file output stream
    fop = FileOutputStream(out_file)

    writer = MarcStreamWriter(fop, "UTF-8")
    written_records = 0

    while reader.hasNext():
        record = reader.next()
        #Get record id for logging.
        raw = record.getVariableField("907")
        rid = raw.getSubfield('a').getData()[1:9]
        #print record
        last_update_value = MarcUtils.getFieldList(record, "907b").toArray()[0]
        logging.debug("Last update for %s is %s." % (rid, last_update_value))
        last_update = convert_date(last_update_value)
        if last_update is None:
          logging.warning("No last update found for %s with %s." % (rid, last_update_value))
        if days_check:
            if last_update >= cutoff:
                writer.write(record)
                written_records += 1
        else:
            if (last_update >= start) and (last_update <= end):
                writer.write(record)
                written_records += 1

    #Close MARC file handle.
    writer.close()
    print>>sys.stderr, '%d updated records written to %s' % (written_records, out_file)
  
      

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
    p.add_option('--output',
               '-o',
               default=None,
               help='Pass in the output directory.'
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
    options, arguments = p.parse_args()
    mfile = os.path.realpath(options.file)
    days = int(options.days)
    main(mfile=mfile,
       output_dir=options.output,
       days=days,
       start=options.start,
       end=options.end)
