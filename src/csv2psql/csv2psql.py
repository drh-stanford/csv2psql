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

import sys
assert sys.version_info >= (2, 6), "Requires python v2.6 or better"

import csv
import os
import os.path
import getopt

_verbose = False

# from PostgreSQL 8.4 documentation
_psql_reserved_words = ["a", "abs", "absent", "according", "ada", "all", "allocate", "alter",
    "analyse", "analyze", "and", "any", "are", "array", "array_agg", "as", "asc",
    "asensitive", "asymmetric", "at", "atomic", "attribute", "attributes",
    "authorization", "avg", "base64", "begin", "bernoulli", "between", "bigint",
    "binary", "blob", "bom", "boolean", "both", "breadth", "by", "c", "call",
    "called", "cardinality", "cascaded", "case", "cast", "catalog_name", "ceil",
    "ceiling", "char", "character", "characters", "character_length",
    "character_set_catalog", "character_set_name", "character_set_schema",
    "char_length", "check", "class_origin", "clob", "close", "coalesce", "cobol",
    "collate", "collation", "collation_catalog", "collation_name",
    "collation_schema", "collect", "column", "columns", "column_name",
    "command_function", "command_function_code", "commit", "condition",
    "condition_number", "connect", "connection_name", "constraint",
    "constraint_catalog", "constraint_name", "constraint_schema", "constructor",
    "contains", "convert", "corr", "corresponding", "count", "covar_pop",
    "covar_samp", "create", "cross", "cube", "cume_dist", "current",
    "current_catalog", "current_date", "current_default_transform_group",
    "current_path", "current_role", "current_schema", "current_time",
    "current_timestamp", "current_transform_group_for_type", "current_user",
    "cursor", "cursor_name", "cycle", "date", "datetime_interval_code",
    "datetime_interval_precision", "day", "deallocate", "dec", "decimal",
    "declare", "default", "deferrable", "defined", "degree", "delete",
    "dense_rank", "depth", "deref", "derived", "desc", "describe", "descriptor",
    "deterministic", "diagnostics", "disconnect", "dispatch", "distinct", "do",
    "double", "drop", "dynamic", "dynamic_function", "dynamic_function_code",
    "each", "element", "else", "empty", "end", "end-exec", "equals", "escape",
    "every", "except", "exclude", "exec", "execute", "exists", "exp", "external",
    "extract", "false", "fetch", "filter", "final", "first_value", "flag",
    "float", "floor", "following", "for", "foreign", "fortran", "found", "free",
    "freeze", "from", "full", "function", "fusion", "g", "general", "generated",
    "get", "global", "go", "goto", "grant", "group", "grouping", "having", "hex",
    "hierarchy", "hold", "hour", "id", "identity", "ignore", "ilike",
    "implementation", "in", "indent", "indicator", "initially", "inner", "inout",
    "insensitive", "insert", "instance", "instantiable", "int", "integer",
    "intersect", "intersection", "interval", "into", "is", "isnull", "join", "k",
    "key_member", "key_type", "lag", "language", "large", "last_value", "lateral",
    "lead", "leading", "left", "length", "like", "like_regex", "limit", "ln",
    "local", "localtime", "localtimestamp", "locator", "lower", "m", "map",
    "match", "matched", "max", "max_cardinality", "member", "merge",
    "message_length", "message_octet_length", "message_text", "method", "min",
    "minute", "mod", "modifies", "module", "month", "more", "multiset", "mumps",
    "namespace", "national", "natural", "nchar", "nclob", "nesting", "new", "nfc",
    "nfd", "nfkc", "nfkd", "nil", "no", "none", "normalize", "normalized", "not",
    "notnull", "nth_value", "ntile", "null", "nullable", "nullif", "number",
    "numeric", "occurrences_regex", "octets", "octet_length", "of", "off",
    "offset", "old", "on", "only", "open", "or", "order", "ordering",
    "ordinality", "others", "out", "outer", "output", "over", "overlaps",
    "overlay", "overriding", "p", "pad", "parameter", "parameter_mode",
    "parameter_name", "parameter_ordinal_position", "parameter_specific_catalog",
    "parameter_specific_name", "parameter_specific_schema", "partition", "pascal",
    "passing", "path", "percentile_cont", "percentile_disc", "percent_rank",
    "placing", "pli", "position", "position_regex", "power", "preceding",
    "precision", "prepare", "primary", "procedure", "public", "range", "rank",
    "reads", "real", "recursive", "ref", "references", "referencing", "regr_avgx",
    "regr_avgy", "regr_count", "regr_intercept", "regr_r2", "regr_slope",
    "regr_sxx", "regr_sxy", "regr_syy", "release", "respect", "result", "return",
    "returned_cardinality", "returned_length", "returned_octet_length",
    "returned_sqlstate", "returning", "returns", "revoke", "right", "rollback",
    "rollup", "routine", "routine_catalog", "routine_name", "routine_schema",
    "row", "rows", "row_count", "row_number", "savepoint", "scale", "schema_name",
    "scope", "scope_catalog", "scope_name", "scope_schema", "scroll", "search",
    "second", "section", "select", "self", "sensitive", "server_name",
    "session_user", "set", "sets", "similar", "size", "smallint", "some",
    "source", "space", "specific", "specifictype", "specific_name", "sql",
    "sqlexception", "sqlstate", "sqlwarning", "sqrt", "start", "state", "static",
    "stddev_pop", "stddev_samp", "structure", "style", "subclass_origin",
    "submultiset", "substring", "substring_regex", "sum", "symmetric", "system",
    "system_user", "t", "table", "tablesample", "table_name", "then", "ties",
    "time", "timestamp", "timezone_hour", "timezone_minute", "to",
    "top_level_count", "trailing", "transactions_committed",
    "transactions_rolled_back", "transaction_active", "transform", "transforms",
    "translate", "translate_regex", "translation", "treat", "trigger",
    "trigger_catalog", "trigger_name", "trigger_schema", "trim", "trim_array",
    "true", "truncate", "uescape", "unbounded", "under", "union", "unique",
    "unknown", "unnamed", "unnest", "untyped", "update", "upper", "uri", "usage",
    "user", "user_defined_type_catalog", "user_defined_type_code",
    "user_defined_type_name", "user_defined_type_schema", "using", "value",
    "values", "varbinary", "varchar", "variadic", "varying", "var_pop",
    "var_samp", "verbose", "when", "whenever", "where", "width_bucket", "window",
    "with", "within", "without", "xml", "xmlagg", "xmlattributes", "xmlbinary",
    "xmlcast", "xmlcomment", "xmlconcat", "xmldeclaration", "xmldocument",
    "xmlelement", "xmlexists", "xmlforest", "xmliterate", "xmlnamespaces",
    "xmlparse", "xmlpi", "xmlquery", "xmlschema", "xmlserialize", "xmltable",
    "xmltext", "xmlvalidate", "year"]


def _mangle_table(s, reserved_words = False):
    '''Mangles an identifer into a psql-safe identifier for a table
with optionally mangling reserved words.

From the PostgreSQL 8.4 manual:

SQL identifiers and key words must begin with a letter (a-z, but also
letters with diacritical marks and non-Latin letters) or an underscore
(_). Subsequent characters in an identifier or key word can be letters,
underscores, digits (0-9), or dollar signs ($). Note that dollar signs are
not allowed in identifiers according to the letter of the SQL standard,
so their use might render applications less portable. The SQL standard
will not define a key word that contains digits or starts or ends with
an underscore, so identifiers of this form are safe against possible
conflict with future extensions of the standard.

The system uses no more than NAMEDATALEN-1 bytes of an identifier; longer
names can be written in commands, but they will be truncated. By default,
NAMEDATALEN is 64 so the maximum identifier length is 63 bytes. If
this limit is problematic, it can be raised by changing the NAMEDATALEN
constant in src/include/pg_config_manual.h.

    >>> _mangle_table('MyTable')
    'mytable'
    >>> _mangle_table('00table')
    'x00table'
    >>> _mangle_table('My Table')
    'my_table'
    >>> _mangle_table('My.Table')
    'my.table'
    >>> _mangle_table('year')
    'year'
    >>> _mangle_table('year', True)
    'year_'
    >>> _mangle_table('a table name much longer than 64 characters blah blah blah blah blah blah blah blah')
    'a_table_name_much_longer_than_64_characters_blah_blah_blah_bla'
    >>>

    '''
    assert s is not None and len(s) > 0
    if reserved_words and s in _psql_reserved_words:
        s = s + "_"
    m = str()
    if s[0].isdigit():
        m += "x"
    for i in s:
        if i.isspace() or i == '_':
            m += "_"
        elif i == '.':
            m += "."
        elif i.isalnum():
            m += i.lower()
    return m[0:62]

def _mangle(s):
    return _mangle_table(s).replace('.', '_')

def _psql_identifier(s):
    '''wraps any reserved word with double quote escapes'''
    k = _mangle(s)
    if k.lower() in _psql_reserved_words:
        return '"%s"' % (k)
    return k

def _isbool(v):
    return str(v).strip().lower() == 'true' or str(v).strip().lower() == 'false'

def _grow_varchar(s):
    '''varchar grows by 80,255,1024

    >>> _grow_varchar(None)
    80
    >>> _grow_varchar("hello")
    80
    >>> _grow_varchar("hello hello hello hello hello" * 5)
    255
    >>> _grow_varchar("hello hello hello hello hello" * 10)
    1024
    >>> _grow_varchar("hello hello hello hello hello" * 100)
    2900

    '''
    if s is None:
        return 80 # default size
    l = len(s)
    if l <= 80:
        return 80
    if l <= 255:
        return 255
    if l <= 1024:
        return 1024
    return l

def _psqlencode(v, dt):
    '''encodes using the text mode of PostgreSQL 8.4 "COPY FROM" command

    >>> _psqlencode('hello "there"', str)
    'hello "there"'
    >>> _psqlencode("hello 'there'", str)
    "hello 'there'"
    >>> _psqlencode('True', int)
    '1'
    >>> _psqlencode(100.1, float)
    '100.1'
    >>> _psqlencode(100.1, int)
    '100'
    >>> _psqlencode('', str)
    ''
    >>> _psqlencode(None, int)
    '\\N'
    >>> _psqlencode("	", str)
    '\\x09'

    '''
    if v is None or v == '':
        return '' if dt == str else '\\N'

    if dt == int:
        if str(v).strip().lower() == 'true':
            return '1'
        if str(v).strip().lower() == 'false':
            return '0'
        return str(int(v))
    if dt == float:
        return str(float(v))
    s = ''
    for c in str(v):
        if ord(c) < ord(' '):
            s += '\\x%02x' % (ord(c))
        else:
            s += c
    return s

def _sniffer(f, maxsniff = -1, datatype = {}):
    '''sniffs out data types'''
    _tbl = dict()

    # initialize data types
    for k in f.fieldnames:
        _k = _mangle(k)
        assert len(_k) > 0
        _tbl[_k] = { 'type': str, 'width': _grow_varchar(None) } # default data type
        if _k in datatype:
            dt = datatype[_k]
            if dt in ['int', 'int4', 'integer']:
                _tbl[_k] = { 'type': int, 'width': 4 }
            elif dt in ['float', 'double', 'float8']:
                _tbl[_k] = { 'type': float, 'width': 8 }
            elif dt in ['text', 'str']:
                _tbl[_k] = { 'type': str, 'width': -1 }

    _need_sniff = False
    for k in f.fieldnames:
        if _mangle(k) not in datatype:
            _need_sniff = True
            break

    # sniff out data types
    if maxsniff <> 0 and _need_sniff:
        i = 0
        for row in f:
            i += 1
            if maxsniff > 0 and i > maxsniff:
                break

            # if _verbose: print >>sys.stderr, 'sniffing row', i, '...', row, _tbl

            # sniff each data field
            for k in f.fieldnames:
                _k = _mangle(k)
                assert len(_k) > 0

                v = row[k]
                assert type(v) == str
                if len(v) == 0:
                    continue # skip empty strings

                if _k in datatype:
                    continue # skip already typed column

                (dt, dw) = (_tbl[_k]['type'], _tbl[_k]['width'])
                try:
                    if (_isbool(v) or int(v) is not None) and not (dt == float):
                        _tbl[_k] = { 'type': int, 'width': 4 }
                except ValueError, e:
                    try:
                        if dt == int: # revert to string
                            _tbl[_k] = { 'type': str, 'width': _grow_varchar(v) }
                        if float(v) is not None:
                            _tbl[_k] = { 'type': float, 'width': 8 }
                    except ValueError, e:
                        if dt == float:
                            _tbl[_k] = { 'type': str, 'width': _grow_varchar(v) }
                        if dt == str and dw < len(v):
                            _tbl[_k] = { 'type': dt, 'width': _grow_varchar(v) }

    return _tbl
    
def _csv2psql(ifn, tablename, 
                fout = sys.stdout, 
                analyze_table = True, 
                cascade = False, 
                create_table = True, 
                datatype = {},
                default_to_null = True, 
                default_user = None, 
                delimiter = ',', 
                force_utf8 = False, 
                load_data = True, 
                maxsniff = -1, 
                pkey = None, 
                quiet = True, 
                schema = None, 
                strip_prefix = True, 
                truncate_table = False, 
                uniquekey = None):
    if schema is None:
        schema = os.getenv('CSV2PSQL_SCHEMA', 'public').strip()
        if schema == '':
            schema = None

    if default_user is None:
        default_user = os.getenv('CSV2PSQL_USER', '').strip()
        if default_user == '':
            default_user = None

    if ifn == '-':
        maxsniff = 0
        create_table = False

    # pass 1
    _tbl = dict()
    if create_table:
        f = csv.DictReader(sys.stdin if ifn == '-' else open(ifn, 'rU'), restval='', delimiter=delimiter)
        _tbl = _sniffer(f, maxsniff, datatype)

    if default_user is not None:
        print >>fout, "SET ROLE", default_user, ";\n"

    # add schema as sole one in search path, and snip table name if starts with schema
    if schema is not None:
        print >>fout, "SET search_path TO %s;" % (schema)
        if strip_prefix and tablename.startswith(schema):
            tablename = tablename[len(schema)+1:]
            while not tablename[0].isalpha():
                tablename = tablename[1:]

    # add explicit client encoding
    if force_utf8:
        print >>fout, "\\encoding UTF8\n"

    if quiet:
        print >>fout, "SET client_min_messages TO ERROR;\n"

    # drop table if we plan to create but not truncate
    if create_table:
        print >>fout, "DROP TABLE IF EXISTS", tablename, "CASCADE;" if cascade else ";"

        print >>fout, "CREATE TABLE", tablename, "(\n\t",
        cols = list()
        for k in f.fieldnames:
            _k = _mangle(k)
            if _k is None or len(_k) < 1:
                continue

            (dt, dw) = (_tbl[_k]['type'], _tbl[_k]['width'])

            if dt == str:
                if dw > 0 and dw <= 1024:
                    sqldt = "VARCHAR(%d)" % (dw)
                else:
                    sqldt = "TEXT"
            elif dt == int:
                if dw > 4:
                    sqldt = "BIGINT"
                else:
                    sqldt = "INTEGER"
            elif dt == float:
                if dw > 4:
                    sqldt = "DOUBLE PRECISION"
                else:
                    sqldt = "REAL"
            else:
                sqldt = "TEXT" # unlimited length

            if not default_to_null:
                sqldt += " NOT NULL"
            cols.append('%s %s' % (_psql_identifier(_k), sqldt))

        print >>fout, ",\n\t".join(cols)
        print >>fout, ");"
        if default_user is not None:
            print >>fout, "ALTER TABLE", tablename, "OWNER TO", default_user, ";"
        if pkey is not None:
            print >>fout, "ALTER TABLE", tablename, "ADD PRIMARY KEY (", ','.join(pkey), ");"
        if uniquekey is not None:
            print >>fout, "ALTER TABLE", tablename, "ADD UNIQUE (", ','.join(uniquekey), ");"

    if truncate_table and not load_data:
        print >>fout, "TRUNCATE TABLE", tablename, ";"

    # pass 2
    if load_data:
        print >>fout, "\COPY %s FROM stdin" % (tablename)
        f = csv.DictReader(sys.stdin if ifn == '-' else open(ifn, 'rU'), delimiter=delimiter)
        for row in f:
            # we have to ensure that we're cleanly reading the input data
            outrow = []
            for k in f.fieldnames:
                assert k in row
                try:
                    _k = _mangle(k)
                    if _k in _tbl and 'type' in _tbl[_k]:
                        dt = _tbl[_k]['type']
                    else:
                        dt = str
                    outrow.append(_psqlencode(row[k], dt))
                except ValueError, e:
                    print >>sys.stderr, 'ERROR:', ifn
                    print >>sys.stderr, k, _k, type(e), e
                    print >>sys.stderr, row
                    sys.exit(1)
            print >>fout, "\t".join(outrow)
        print >>fout, "\\."

    if load_data and analyze_table:
        print >>fout, "ANALYZE", tablename, ";"

    return _tbl

def _usage():
    print '''%s\n\nWritten by %s''' % (__doc__, __author__)

_schemas = [ 'public' ] 

_datatypes = ['int4', 'float8', 'str', 'integer', 'float', 'double', 'text']
_verbose = True

def csv2psql(filename, tablename, **flags):
    ''' Main entry point. Converts CSV `filename` into PostgreSQL `tablename`.
    To detect data types for each field, it reads `flags.maxsniff` rows in
    the CSV file. If `flags.maxsniff` = -1 then it reads the entire CSV file.
    Set `maxsniff` = 0 to disable data type detection.
    '''
    _csv2psql(filename, tablename, **flags)

def main(argv = None):
    '''command-line interface'''
    if argv is None:
        argv = sys.argv[1:]
    try:
        # init default flags
        flags = dict()
        flags['maxsniff']= 1000

        opts, args = getopt.getopt(argv, "ak:s:q", ["help", "version", "schema=", "key=", "unique=", "cascade", "append", "utf8", "sniff=", "datatype=", "role="])
        for o, a in opts:
            if o in ("--version"):
                print __version__
                return 0
            elif o in ("--help"):
                _usage()
                return 0
            elif o in ("--cascade"):
                flags['cascade'] = True
            elif o in ("-a", "--append"):
                flags['create_table'] = False
                flags['truncate_table'] = False
                flags['load_data'] = True
                flags['maxsniff'] = 0
            elif o in ("-s", "--schema"):
                flags['schema'] = a
            elif o in ("--role"):
                flags['default_user'] = a
            elif o in ("--sniff"):
                flags['maxsniff'] = int(a)
            elif o in ("-k", "--key"):
                flags['pkey'] = a.split(':')
            elif o in ("--unique"):
                flags['uniquekey'] = a.split(':')
            elif o in ("--utf8"):
                flags['force_utf8'] = True
            elif o in ("--datatype"):
                if 'datatype' not in flags:
                    flags['datatype'] = dict()
                (k, v) = a.split(':')
                v = v.strip().lower()
                if v in _datatypes:
                    for k in [_mangle(_k) for _k in k.split(',')]:
                        flags['datatype'][k] = v
                else:
                    raise getopt.GetoptError('unknown data type %s (use %s)' % (v, _datatypes))
            elif o in ("-q"):
                _verbose = False
            else:
                raise getopt.GetoptError('unknown option %s' % (o))

        if len(args) < 1:
            _usage()
            return -1
        # with a single argument -- we guess the table name
        elif len(args) == 1:
            fn = args[0]
            if fn == '-':
                raise getopt.GetoptError('cannot guess tablename')

            tablename = os.path.splitext(os.path.basename(fn))[0]
            if 'schema' not in flags:
                for s in _schemas:
                    if tablename.startswith(s):
                        flags['schema'] = s
                        break

            print flags;
            csv2psql(fn, _mangle_table(tablename), **flags)
            return 0
        elif len(args) == 2:
            fn = args[0]
            tablename = args[1]
            print flags;
            csv2psql(fn, _mangle_table(tablename), **flags)
            return 0
        else:
            assert False, 'notreached'
    except getopt.GetoptError, err:
        print >>sys.stderr, 'ERROR:', str(err), "\n\n"
        _usage()
        return -1

if __name__ == '__main__':
    sys.exit(main())
