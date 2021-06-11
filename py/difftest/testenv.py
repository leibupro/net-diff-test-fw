import os
import sys

from distutils import util as dstutl
from difftest.cfg import PlatformCfg, \
                         GeneratorCfg, \
                         RecInterfaceCfg, \
                         RecorderCfg, \
                         CmpCfg, \
                         ComparatorEntry
from difftest.util import create_directory, \
                          create_timestamp_str, \
                          get_cfg_value, \
                          get_dev_null, \
                          parse_literal_string

dump_location_base = None

# Golden Platform ...
def get_gp_cfg():
    platf_cfg = PlatformCfg(
        get_cfg_value( 'GOLDEN_PLATFORM', 'ip' ),
        get_cfg_value( 'GOLDEN_PLATFORM', 'netmask' ) )
    return platf_cfg


# Platform Under Test ...
def get_put_cfg():
    platf_cfg = PlatformCfg(
        get_cfg_value( 'PLATFORM_UNDER_TEST', 'ip' ),
        get_cfg_value( 'PLATFORM_UNDER_TEST', 'netmask' ) )
    return platf_cfg


# Pcap file dump location ...
def get_pcap_dump_loc():
    global dump_location_base
    if dump_location_base is None:
        location = get_cfg_value( 'PCAP_DUMP_LOCATION', 'base_path' )
        ts = create_timestamp_str()
        location += ( '/' + ts + '_test_suite_run' )
        create_directory( location )
        dump_location_base = location
    return dump_location_base


# Generator configuration towards golden platform
def get_gp_gen_cfg( platf_cfg ):
    gen_if_name = get_cfg_value( 'GEN_INTERFACE_GP', 'name' )
    cfg = get_gen_cfg( platf_cfg, gen_if_name )
    return cfg


# Generator configuration towards platform under test
def get_put_gen_cfg( platf_cfg ):
    gen_if_name = get_cfg_value( 'GEN_INTERFACE_PUT', 'name' )
    cfg = get_gen_cfg( platf_cfg, gen_if_name )
    return cfg


# assemble a generator configuration ...
def get_gen_cfg( platf_cfg, gen_if_name ):
    out = None
    err = None
    gen_cfg = None
    silence = get_cfg_value( 'SILENCE_OUTPUT', 'generators' )
    try:
        silence = dstutl.strtobool( silence )
    except ( ValueError, ) as e:
        sys.stderr.write( str( e ) + '\n' )
        sys.exit( os.EX_USAGE )
    if silence:
        out = get_dev_null()
        err = get_dev_null()
    else:
        out = sys.stdout
        err = sys.stderr
    gen_cfg = GeneratorCfg(
        gen_if_name,
        platf_cfg,
        exec_time = None,
        gen_cmd = None,
        stdout = out,
        stderr = err )
    return gen_cfg


def chk_timing_rngs( parsed_literal ):
    ret_val = False
    # None is considered valid
    if parsed_literal is None:
        ret_val = True
    elif type( parsed_literal ) == list:
        res = [ type( x ) == tuple for x in parsed_literal ]
        if all( res ):
            res = [ len( x ) == 2 for x in parsed_literal ]
            if all( res ):
                res = [ all ( [ type( y ) == int or \
                                type( y ) == float \
                                for y in x ] ) \
                        for x in parsed_literal ]
                if all( res ):
                    ret_val = True
    return ret_val


def assemble_gp_rec_ifs():
    rec_if_0_name = get_cfg_value( 'REC_INTERFACE_GP_0', 'name' )
    rec_if_1_name = get_cfg_value( 'REC_INTERFACE_GP_1', 'name' )
    single_if_bool_str = get_cfg_value( 'TAP_DEVICE_GP',
                                        'single_interface' )
    rec_ifs = assemble_rec_ifs( rec_if_0_name, single_if_bool_str,
                                'GP', rec_if_1_name )
    return rec_ifs


def assemble_put_rec_ifs():
    rec_if_0_name = get_cfg_value( 'REC_INTERFACE_PUT_0', 'name' )
    rec_if_1_name = get_cfg_value( 'REC_INTERFACE_PUT_1', 'name' )
    single_if_bool_str = get_cfg_value( 'TAP_DEVICE_PUT',
                                        'single_interface' )
    rec_ifs = assemble_rec_ifs( rec_if_0_name, single_if_bool_str,
                                'PUT', rec_if_1_name )
    return rec_ifs


def assemble_rec_ifs( rec_if_0_name, single_if_bool_str,
                      target_str, rec_if_1_name = None ):
    ret_val = None
    if_cfg_0 = RecInterfaceCfg(
        rec_if_0_name,
        target_str,
        None,
        filter_expr = None )
    try:
        single_if = dstutl.strtobool( single_if_bool_str )
    except ( ValueError, ) as e:
        sys.stderr.write( str( e ) + '\n' )
        sys.exit( os.EX_USAGE )
    if single_if:
        ret_val = ( if_cfg_0, )
    else:
        if_cfg_1 = RecInterfaceCfg(
            rec_if_1_name,
            target_str,
            None,
            filter_expr = None )
        ret_val = ( if_cfg_0, if_cfg_1 )
    return ret_val


def get_gp_rec_cfg():
    rec_ifs = assemble_gp_rec_ifs()
    rec_cfg = RecorderCfg( rec_ifs, None )
    return rec_cfg


def get_put_rec_cfg():
    rec_ifs = assemble_put_rec_ifs()
    rec_cfg = RecorderCfg( rec_ifs, None )
    return rec_cfg


def mk_rec_dir_tree_and_f_expr( cmd_name, rec_cfg, rec_filter_expr,
                                rec_pause_before_stop_str ):
    cmd_dump_dir = ( get_pcap_dump_loc() + os.path.sep + cmd_name )
    create_directory( cmd_dump_dir )
    try:
        rec_pause_before_stop = int( rec_pause_before_stop_str,
                                     base = 10 )
    except ( ValueError, ) as e:
        sys.stderr.write( str( e ) + '\n' )
        sys.exit( os.EX_USAGE )
    rec_cfg.set_pause_before_stop( rec_pause_before_stop )
    rec_ifs = rec_cfg.get_rec_ifs()
    new_rec_ifs = ()
    assert( len( rec_ifs ) <= 2 )
    char = 0x41
    for rec_if in rec_ifs:
        wr_path = ( cmd_dump_dir + os.path.sep + chr( char ) )
        char += 1
        create_directory( wr_path )
        rec_if.set_wr_path( wr_path )
        rec_if.set_filter_expr( rec_filter_expr )
        new_rec_ifs += ( rec_if, )
    rec_cfg.set_rec_ifs( new_rec_ifs )
    return rec_cfg


# Initial comparator configuration setup.
def get_initial_cmp_cfg( recorder_service ):
    cmp_cfg = CmpCfg()
    rec_sub_svcs = recorder_service.get_sub_services()
    rec_ifs_lst = []
    if len( rec_sub_svcs ) != 2:
        sys.stderr.write( 'Recorder must contain only two ' + \
                          'sub services. GP and PUT\n' )
        sys.exit( os.EX_USAGE )
    for sub_svc in rec_sub_svcs:
        rec_ifs_lst.append( sub_svc.get_cfg().get_rec_ifs() )
    assert( len( rec_ifs_lst[ 0 ] ) == len( rec_ifs_lst[ 1 ] ) )
    assert( ( len( rec_ifs_lst[ 0 ] ) > 0 ) and \
            ( len( rec_ifs_lst[ 0 ] ) <= 2 ) )
    pcap_exp_loc = None
    pcap_act_loc = None
    for idx in range( len( rec_ifs_lst[ 0 ] ) ):
        pcap_exp_loc = rec_ifs_lst[ 0 ][ idx ].get_pcap_path()
        pcap_act_loc = rec_ifs_lst[ 1 ][ idx ].get_pcap_path()
        cmp_cfg.add_cmp_pcap_pair( ( pcap_exp_loc, pcap_act_loc ) )
        cmp_cfg.add_cmp_rpt_location(
            os.path.dirname( pcap_exp_loc ) )
    assert( len( cmp_cfg.get_cmp_pair_pcap_locations() ) == \
            len( cmp_cfg.get_cmp_pair_pcap_locations() ) )
    return cmp_cfg


def inject_timing_ranges( cmp_cfg, section_str ):
    trs_str_gp = get_cfg_value( section_str, 'time_rngs_gp' )
    trs_str_put = get_cfg_value( section_str, 'time_rngs_put' )
    trs_gp = parse_literal_string( trs_str_gp )
    trs_put = parse_literal_string( trs_str_put )
    if chk_timing_rngs( trs_gp ) and chk_timing_rngs( trs_put ):
        cmp_cfg.set_inter_pkt_times_gp( trs_gp )
        cmp_cfg.set_inter_pkt_times_put( trs_put )
    else:
        sys.stderr.write( 'The parsing of the valid timing range ' + \
                          'values failed. This is the end here.\n' )
        sys.exit( os.EX_USAGE )
    return cmp_cfg


# ****************************************************************** #
#     Protocol specific config parameters                            #
# ****************************************************************** #


# Generator command injections for different protocol generators ...
def inject_icmp_gen_cmd_0( gen_cfg ):
    cmd_prefix = get_cfg_value( 'ICMP_GEN_CMD_0', 'prefix' )
    cmd = get_cfg_value( 'ICMP_GEN_CMD_0', 'cmd_str' )
    gen_timeout = get_cfg_value( 'ICMP_GEN_CMD_0', 'timeout' )
    try:
        gen_timeout = int( gen_timeout, base = 10 )
    except ( ValueError, ) as e:
        sys.stderr.write( str( e ) + '\n' )
        sys.exit( os.EX_USAGE )
    # command string platform specific substitutions ...
    gen_cmd = ( cmd_prefix + ' ' + cmd ) % \
              ( gen_cfg.get_gen_if(),
                gen_cfg.get_platform_cfg().get_ip() )
    gen_cmd = gen_cmd.split( ' ' )
    gen_cmd = [ x for x in gen_cmd if x != '' ]
    gen_cfg.set_gen_cmd( gen_cmd )
    gen_cfg.set_exec_time( gen_timeout )
    return gen_cfg


# Recorder command injections for different protocol recorders ...
def inject_icmp_rec_cmd_0( rec_cfg ):
    cmd_name = get_cfg_value( 'ICMP_GEN_CMD_0', 'name' )
    rec_pause_before_stop_str = get_cfg_value( 'ICMP_GEN_CMD_0',
                                               'pause_before_stop' )
    rec_filter_expr = get_cfg_value( 'ICMP_GEN_CMD_0', 'filter_expr' )
    rec_cfg = mk_rec_dir_tree_and_f_expr( cmd_name, rec_cfg,
                                          rec_filter_expr,
                                          rec_pause_before_stop_str )
    return rec_cfg


# Timing ranges injection for the icmp 0 test case ...
def inject_icmp_cmd_0_trs( cmp_cfg ):
    cmp_cfg = inject_timing_ranges( cmp_cfg, 'ICMP_GEN_CMD_0' )
    return cmp_cfg

# ****************************************************************** #

# Timing ranges injection for the TLS handshake test case ...
def inject_tlshs_trs( cmp_cfg ):
    cmp_cfg = inject_timing_ranges( cmp_cfg, 'TLS_HS_0' )
    return cmp_cfg


# Generator command injections for different protocol generators ...
def inject_tlshs_gen_cmd( gen_cfg ):
    cmd_prefix = get_cfg_value( 'TLS_HS_0', 'prefix' )
    cmd = get_cfg_value( 'TLS_HS_0', 'cmd_str' )
    gen_timeout = get_cfg_value( 'TLS_HS_0', 'timeout' )
    try:
        gen_timeout = int( gen_timeout, base = 10 )
    except ( ValueError, ) as e:
        sys.stderr.write( str( e ) + '\n' )
        sys.exit( os.EX_USAGE )
    # command string platform specific substitutions ...
    gen_cmd = ( cmd_prefix + ' ' + cmd ) % \
              ( gen_cfg.get_platform_cfg().get_ip(), )
    gen_cfg.set_gen_cmd( gen_cmd.split( ' ' ) )
    gen_cfg.set_exec_time( gen_timeout )
    return gen_cfg


# Recorder command injections for different protocol recorders ...
def inject_tlshs_rec_cmd( rec_cfg ):
    cmd_name = get_cfg_value( 'TLS_HS_0', 'name' )
    rec_pause_before_stop_str = get_cfg_value( 'TLS_HS_0',
                                               'pause_before_stop' )
    rec_filter_expr = get_cfg_value( 'TLS_HS_0', 'filter_expr' )
    rec_cfg = mk_rec_dir_tree_and_f_expr( cmd_name, rec_cfg,
                                          rec_filter_expr,
                                          rec_pause_before_stop_str )
    return rec_cfg

