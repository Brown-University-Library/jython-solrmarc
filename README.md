jython-solrmarc
===============

Using SolrMarc with Jython. 

This is a basic setup for working with [SolrMarc](http://code.google.com/p/solrmarc/) using Jython.  In this example, the [Stanford SolrMarc](https://github.com/solrmarc/stanford-solr-marc) version is pulled in as a git submodule.     


* Update and build solrmarc
 * cd solrmarc
 * git pull
 * ant

* Set your CLASSPATH
 * source .set_env.sh

* Run the sample indexing script:
 * jython index.py data/iii_sample.mrc