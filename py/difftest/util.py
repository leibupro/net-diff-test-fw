
import os
import sys
import logging
import datetime as dt
import configparser as cp
import ast


# Global declaration of the log level
LOG_LEVEL = logging.INFO
LOG_FMT_STR = '%(asctime)s [%(threadName)-' + \
    '12.12s] [%(levelname)-5.5s]  %(message)s'

# Test setup ini file location
INI_PATH = './test_setup.ini'


def get_logger( logger_name = __name__ ):
    log_formatter = logging.Formatter( LOG_FMT_STR )
    log = logging.getLogger( logger_name )
    console_handler = logging.StreamHandler( sys.stdout )
    console_handler.setFormatter( log_formatter )
    log.addHandler( console_handler )
    log.setLevel( LOG_LEVEL )
    return log


def get_report_logger( file_path, also_stdout = True ):
    log_formatter = logging.Formatter( LOG_FMT_STR )
    log = logging.getLogger( ( 'Logger ' + file_path ) )
    log_file = ( file_path + '/report.txt' )
    file_handler = logging.FileHandler( log_file )
    file_handler.setFormatter( log_formatter )
    log.addHandler( file_handler )
    if also_stdout:
        console_handler = logging.StreamHandler( sys.stdout )
        console_handler.setFormatter( log_formatter )
        log.addHandler( console_handler )
    log.setLevel( LOG_LEVEL )
    os.chmod( log_file, 0o666 )
    return log


def tear_down_report_logger( log ):
    handlers = log.handlers[ : ]
    for handler in handlers:
        handler.flush()
        handler.close()
        log.removeHandler( handler )


def print_failwhale( out = sys.stderr, mute = False ):
    fw_str = \
        ( '\n\n' +
          \
          \
          '           ▄██████████████▄▐█▄▄▄▄█▌\n' +
          '           ██████▌▄▌▄▐▐▌███▌▀▀██▀▀\n' +
          '           ████▄█▌▄▌▄▐▐▌▀███▄▄█▌\n' +
          '           ▄▄▄▄▄██████████████▀\n\n'
          \
          \
        )
    if not mute:
        print( fw_str, file = out )
    return fw_str


def log_failwhale( log_fn ):
    fw_str = print_failwhale( mute = True )
    tokens = fw_str.split( '\n' )
    for tok in tokens:
        log_fn( tok )


def print_ascii_fail( out = sys.stderr, mute = False ):
    fail_str = \
        ( '\n\n' +
    '    8888888888     d8888 8888888 888      \n' +
    '    888           d88888   888   888      \n' +
    '    888          d88P888   888   888      \n' +
    '    8888888     d88P 888   888   888      \n' +
    '    888        d88P  888   888   888      \n' +
    '    888       d88P   888   888   888      \n' +
    '    888      d8888888888   888   888      \n' +
    '    888     d88P     888 8888888 88888888 \n\n'
        )
    if not mute:
        print( fail_str, file = out )
    return fail_str


def log_ascii_fail( log_fn ):
    p_str = print_ascii_fail( mute = True )
    tokens = p_str.split( '\n' )
    for tok in tokens:
        log_fn( tok )


def print_pass( out = sys.stdout, mute = False ):
    p_str = \
        ( '\n\n' +
    '      ___         ___           ___           ___      \n' +
    '     /\  \       /\  \         /\__\         /\__\     \n' +
    '    /::\  \     /::\  \       /:/ _/_       /:/ _/_    \n' +
    '   /:/\:\__\   /:/\:\  \     /:/ /\  \     /:/ /\  \   \n' +
    '  /:/ /:/  /  /:/ /::\  \   /:/ /::\  \   /:/ /::\  \  \n' +
    ' /:/_/:/  /  /:/_/:/\:\__\ /:/_/:/\:\__\ /:/_/:/\:\__\ \n' +
    ' \:\/:/  /   \:\/:/  \/__/ \:\/:/ /:/  / \:\/:/ /:/  / \n' +
    '  \::/__/     \::/__/       \::/ /:/  /   \::/ /:/  /  \n' +
    '   \:\  \      \:\  \        \/_/:/  /     \/_/:/  /   \n' +
    '    \:\__\      \:\__\         /:/  /        /:/  /    \n' +
    '     \/__/       \/__/         \/__/         \/__/     \n\n'
        )
    if not mute:
        print( p_str, file = out )
    return p_str


def log_pass( log_fn ):
    p_str = print_pass( mute = True )
    tokens = p_str.split( '\n' )
    for tok in tokens:
        log_fn( tok )


def get_dev_null():
    f = open( os.devnull, 'w' )
    return f


def create_directory( path ):
    if not os.path.isdir( path ) and not os.path.isfile( path ):
        try:
            os.mkdir( path )
            os.chmod( path, 0o777 )
        except ( PermissionError, FileExistsError ) as e:
            sys.stderr.write( str( e ) + '\n' )
            sys.exit( os.EX_OSERR )


def create_timestamp_str():
    now = dt.datetime.now()
    ts = now.strftime( '%Y-%m-%d---T-%H-%M-%S' ) + \
         ( '-%03d' % ( now.microsecond / 1000 ) )
    return ts


def get_cfg_value( section, property_name ):
    ret_val = ''
    config = cp.ConfigParser( allow_no_value = True )
    if len( config.read( INI_PATH ) ) != 1:
        sys.stderr.write( 'Something went wrong. Is the test ' + \
                          'setup ini file available in the ' + \
                          'working directory?\n' )
        sys.exit( os.EX_UNAVAILABLE )
    try:
        ret_val = config.get( section, property_name )
    except ( cp.NoSectionError, cp.NoOptionError,
             cp.InterpolationSyntaxError ) as e:
        sys.stderr.write( str( e ) + '\n' )
        sys.exit( os.EX_USAGE )
    return ret_val


def parse_literal_string( ini_string ):
    result = None
    try:
        result = ast.literal_eval( ini_string )
    except ( Exception, ) as e:
        sys.stderr.write( str( e ) + '\n' )
        sys.exit( os.EX_USAGE )
    return result

