'''
############################################################

                             +
                ---====D                        @
       o                    *
                    *              o
            |
           -O-                         =( =         +
      +     |                   *
                   ____     ________
                  /  _/__  / __/ __/    .
                 _/ // _ \/ _/_\ \             +  .
        *       /___/_//_/___/___/             |
                                       -O-         @
      +                                |
                      *
                   ,      .
           .    `
       @                +    `~---~~`           *

                   *       .            o         +


    Institute of Embedded Systems
    Zurich University of Applied Sciences
    8401 Winterthur, Switzerland


    File:         cfg.py


    Purpose:      This module contains
                  the configuration data
                  classes which are used
                  from the components
                  of the differential
                  testing framework.


    Remarks:      -


    Author(s):    P. Leibundgut <leiu@zhaw.ch>


    Date:         12/2020


############################################################
'''

class GeneratorCfg( object ):
    def __init__( self, gen_if, platform_cfg,
                  exec_time = None, gen_cmd = None,
                  stdout = None, stderr = None ):
        self.__gen_if       = gen_if
        # If the execution time is zero (0) the
        # generator process is assumed to be
        # self terminating. Unit is seconds [s].
        self.__exec_time    = exec_time
        self.__platform_cfg = platform_cfg
        self.__gen_cmd      = gen_cmd
        self.__stdout       = stdout
        self.__stderr       = stderr


    def get_gen_if( self ):
        return self.__gen_if


    def get_exec_time( self ):
        return self.__exec_time


    def get_platform_cfg( self ):
        return self.__platform_cfg


    def get_gen_cmd( self ):
        return self.__gen_cmd


    def get_gen_stdout( self ):
        return self.__stdout


    def get_gen_stderr( self ):
        return self.__stderr


    def set_gen_cmd( self, gen_cmd ):
        self.__gen_cmd = gen_cmd


    def set_exec_time( self, exec_time ):
        self.__exec_time = exec_time



class RecInterfaceCfg( object ):
    def __init__( self, if_name, target_str, wr_path,
                  socket_layer = 2,
                  filter_expr = None ):
        self.__if_name      = if_name
        self.__target_str   = target_str
        self.__wr_path      = wr_path
        self.__socket_layer = socket_layer
        self.__filter_expr  = filter_expr
        self.__pcap_path    = None


    def get_if_name( self ):
        return self.__if_name


    def get_target_str( self ):
        return self.__target_str


    def get_wr_path( self ):
        return self.__wr_path


    def get_socket_layer( self ):
        return self.__socket_layer


    def get_filter_expr( self ):
        return self.__filter_expr


    def get_pcap_path( self ):
        return self.__pcap_path


    def set_wr_path( self, wr_path ):
        self.__wr_path = wr_path


    def set_filter_expr( self, filter_expr ):
        self.__filter_expr = filter_expr


    def set_pcap_path( self, pcap_path ):
        self.__pcap_path = pcap_path



class RecorderCfg( object ):
    def __init__( self, rec_ifs,
                  pause_before_stop ):
        self.__rec_ifs           = rec_ifs
        self.__pause_before_stop = pause_before_stop


    def get_rec_ifs( self ):
        return self.__rec_ifs


    def get_pause_before_stop( self ):
        return self.__pause_before_stop


    def set_rec_ifs( self, rec_ifs ):
        self.__rec_ifs = rec_ifs


    def set_pause_before_stop( self, pause_before_stop ):
        self.__pause_before_stop = pause_before_stop



class ComparatorEntry( object ):
    def __init__( self, scapy_type, field_getters,
                  pkt_cmp_fn = None ):
        self.__scapy_type = scapy_type
        # A n tuple of function pointers (or anonymous functions)
        # in order to extract the wanted fields from a specific
        # network packet.
        self.__field_getters = field_getters
        self.__pkt_cmp_fn = pkt_cmp_fn


    def get_scapy_type( self ):
        return self.__scapy_type


    def get_field_getters( self ):
        return self.__field_getters


    def get_pkt_cmp_fn( self ):
        return self.__pkt_cmp_fn



class CmpCfg( object ):
    def __init__( self ):
        self.__cmp_pair_pcap_locations = []
        self.__cmp_rpt_locations = []
        self.__cmp_entries = []
        self.__inter_pkt_times_gp = None
        self.__inter_pkt_times_put = None


    def get_cmp_pair_pcap_locations( self ):
        return self.__cmp_pair_pcap_locations


    def get_cmp_rpt_locations( self ):
        return self.__cmp_rpt_locations


    def get_cmp_entries( self ):
        return self.__cmp_entries


    def get_inter_pkt_times_gp( self ):
        return self.__inter_pkt_times_gp


    def get_inter_pkt_times_put( self ):
        return self.__inter_pkt_times_put


    def add_cmp_entry( self, cmp_entry ):
        self.__cmp_entries.append( cmp_entry )


    def add_cmp_pcap_pair( self, cmp_pcap_pair ):
        self.__cmp_pair_pcap_locations.append( cmp_pcap_pair )


    def add_cmp_rpt_location( self, rpt_location ):
        self.__cmp_rpt_locations.append( rpt_location )


    def set_inter_pkt_times_gp( self, inter_pkt_times_gp ):
        self.__inter_pkt_times_gp = inter_pkt_times_gp


    def set_inter_pkt_times_put( self, inter_pkt_times_put ):
        self.__inter_pkt_times_put = inter_pkt_times_put



class PlatformCfg( object ):
    def __init__( self, ip, netmask,
                  port = None, mac = None ):
        self.__mac     = mac
        self.__ip      = ip
        self.__netmask = netmask
        self.__port    = port


    def get_mac( self ):
        return self.__mac


    def get_ip( self ):
        return self.__ip


    def get_netmask( self ):
        return self.__netmask


    def get_port( self ):
        return self.__port

