"""
Use SolrMarc from Jython.  Basic example.

Increase heap size:
jython -J-Xmx4096

"""
import glob
import sys
import os

#BASE_DIR directory from project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Add Java classes
from java.lang import RuntimeException, String
from java.io import InputStream, OutputStream
from java.io import File, FileInputStream, ByteArrayOutputStream, FileOutputStream

#marc4j
from org.marc4j import MarcStreamReader, MarcPermissiveStreamReader, MarcStreamWriter
from org.marc4j import ErrorHandler

#SolrMarc
from org.solrmarc.index import SolrIndexer
from org.solrmarc.tools import MarcUtils, CallNumUtils, SolrMarcIndexerException
from org.solrmarc.tools.MarcUtils import *

#Properties files.  These are default Blacklight properties files. 
marc_prop = os.path.join(BASE_DIR, 'config/index.properties')
#This needs to be a list
translation_maps = [os.path.join(BASE_DIR, 'config/translation_maps')]

#A sample indexer.  Methods here overide or extend methods in SolrIndexer.
class MyIndexer(SolrIndexer):
	def __init__(self):
		super(MyIndexer, self).__init__(marc_prop,
										translation_maps)
	def getRecordId(self, record):
		"""
		Example method.  Reads a record ID.  Could be done in a property map but
		will do here for demonstration purposes.
		"""
		raw = record.getVariableField("907")
		rid = raw.getSubfield('a').getData()[1:9]
		return rid

#Read MARC file from command line.
infile = sys.argv[1]
inpath, inname = os.path.split(infile)
f = FileInputStream(infile)
#lifted from https://github.com/billdueber/marc_marc4j/blob/master/lib/marc/marc4j/reader.rb
reader = MarcPermissiveStreamReader(f, True, False, "BESTGUESS")
error_handle = ErrorHandler()

#instantiate your indexer class that inherits from the SolrIndexer
idx = MyIndexer()

#Loop through MARC records
while (reader.hasNext()):
	record = reader.next()
	#Our getRecordId method.
	print idx.getRecordId(record)
	d = idx.createFldNames2ValsMap(record, error_handle)
	for field in d.entrySet():
		#Print the solr field and value.
		print field.key, field.value

