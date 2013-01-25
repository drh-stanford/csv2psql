#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Converts a CSV file into a PostgreSQL table.

Usage: csv2psql.py [options] ( input.csv | - ) [tablename] | psql

options include:
--schema=name   use name as schema, and strip table name if needed
--role=name     use name as role for database transaction
--key=a:b:c     create a primary key using columns named a, b, c.
--unique=a:b:c  create a unique index using columns named a, b, c.
--append        skips table creation and truncation, inserts only
--cascade       drops tables with cascades
--sniff=N       limit field type detection to N rows (default: 1000)
--utf8          force client encoding to UTF8
--datatype=name[,name]:type 
                sets the data type for field NAME to TYPE

environment variables:
CSV2PSQL_SCHEMA      default value for --schema
CSV2PSQL_ROLE        default value for --role
'''
__author__ = "Darren Hardy <hardy@nceas.ucsb.edu>"
__version__ = '0.4.2'
__credits__ = "Copyright (c) 2011-2013 NCEAS (UCSB). All rights reserved."

from csv2psql import csv2psql
__all__ = [ 'csv2psql' ]
