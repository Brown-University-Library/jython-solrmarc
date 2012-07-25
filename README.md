jython-solrmarc
===============

Using SolrMarc with Jython. 

This is a basic setup for working with [SolrMarc](http://code.google.com/p/solrmarc/) using Jython.   

*Build solr-marc
** cd stanford-solr-marc
** ant
** stanford-solr-marc/dist/
** stanford-solr-marc/dist/SolrMarc.jar

* Setup a virtualenv
** virtualenv -p jython env
* Install jip
** pip install jip
* Install JSONObject
** jip install net.sf.json-lib:json-lib:2.4

* Run the sample indexing script