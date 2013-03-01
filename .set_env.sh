#!/bin/bash
path=`pwd`/lib/*:`pwd`/solrmarc/dist/*:`pwd`/solrmarc/dist/lib/*
export CLASSPATH=$CLASSPATH:$path
