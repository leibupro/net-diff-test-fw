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


    File:         bases.py


    Purpose:      This module contains
                  the base classes for
                  the components which
                  are used for the
                  differential testing.
                  The definition of
                  abstract methods can
                  be seen as interface
                  definitions where the
                  derivatives have to
                  provide a concrete
                  implementation of the
                  absract methods.


    Remarks:      - Uses the (AB)stract (C)lasses
                    abc module from the Python
                    standard library.


    Author(s):    P. Leibundgut <leiu@zhaw.ch>


    Date:         12/2020


############################################################
'''

import os
import sys
import signal as sig
import subprocess as sp
import time
import logging
from abc import ABC, abstractmethod
from scapy.all import conf, AsyncSniffer, wrpcap, rdpcap
from difftest.util import get_report_logger, log_ascii_fail, \
                          log_pass, tear_down_report_logger
from difftest.testenv import get_initial_cmp_cfg


ERR_TEXT_ABS_METHOD_CALL = 'Mehtod must be implemented ' + \
                           'in derived class.'


class Base( ABC ):
    def __init__( self, log, cfg ):
        self._log = log
        self._cfg = cfg


    def get_cfg( self ):
        return self._cfg


    @abstractmethod
    def start( self ):
        raise NotImplementedError( ERR_TEXT_ABS_METHOD_CALL )


    @abstractmethod
    def stop( self ):
        raise NotImplementedError( ERR_TEXT_ABS_METHOD_CALL )



class DiffTestComponentBase( Base ):
    def __init__( self, log, cfg ):
        super().__init__( log, cfg )



class DiffTestComparatorBase( Base ):
    def __init__( self, log, cfg ):
        super().__init__( log, cfg )


    @abstractmethod
    def setup( self, recorder_service ):
        raise NotImplementedError( ERR_TEXT_ABS_METHOD_CALL )


    @abstractmethod
    def enrich_cmp_cfg( self ):
        if self._cfg is None:
            self._log.error( 'Comparator configuration must not ' + \
                             'be None at this stage.' )
            return False
        else:
            return True


    @abstractmethod
    def _cmp( self, a, b ):
        raise NotImplementedError( ERR_TEXT_ABS_METHOD_CALL )


    @abstractmethod
    def _eq( self, a, b ):
        raise NotImplementedError( ERR_TEXT_ABS_METHOD_CALL )


    def _ne( self, a, b ):
        return not self._eq( a, b )



class TestCaseBase( ABC ):
    def __init__( self, log ):
        self._log = log
        self._gen_service = None
        self._rec_service = None
        self._cmp_service = None


    def get_gen_service( self ):
        return self._gen_service


    def get_rec_service( self ):
        return self._rec_service


    def get_cmp_service( self ):
        return self._cmp_service


    @abstractmethod
    def run( self, bundle_name = 'John Doe' ):
        self._log.info( 'Starting %s case against Golden Platform.' \
                        % bundle_name )
        self._rec_service.start( target = 'GP' )
        self._gen_service.start( target = 'GP' )
        self._rec_service.stop( target = 'GP' )

        self._log.info( ( 'Starting %s case against ' + \
                          'Platform Under Test.' ) \
                        % bundle_name )
        self._rec_service.start( target = 'PUT' )
        self._gen_service.start( target = 'PUT' )
        self._rec_service.stop( target = 'PUT' )

        self._log.info( 'Setting up comparator configuration' )
        if self._rec_service is not None:
            self._cmp_service.setup( self._rec_service )
        else:
            self._log.error( 'Recorder service must not be None at ' +
                             'this stage.' )
        self._cmp_service.start()


    @abstractmethod
    def unrun( self, bundle_name = 'John Doe' ):
        self._log.info( 'Stopping %s case against Golden Platform.' \
                        % bundle_name )
        self._gen_service.stop( target = 'GP' )
        self._rec_service.stop( target = 'GP' )
        self._log.info( ( 'Stopping %s case against ' + \
                          'Platform Under Test.' ) \
                        % bundle_name )
        self._gen_service.stop( target = 'PUT' )
        self._rec_service.stop( target = 'PUT' )
        self._cmp_service.stop()



class Generator( DiffTestComponentBase ):
    def __init__( self, log, cfg ):
        super().__init__( log, cfg )
        self.__proc = None


    @abstractmethod
    def start( self ):
        cmd = self._cfg.get_gen_cmd()
        p_stdout = self._cfg.get_gen_stdout()
        p_stderr = self._cfg.get_gen_stderr()
        self.__proc = sp.Popen( cmd, stdout = p_stdout,
                                stderr = p_stderr )
        if self._cfg.get_exec_time() == 0:
            self.__proc.wait()
        else:
            if self._cfg.get_exec_time() > 0:
                time.sleep( self._cfg.get_exec_time() )
            else:
                self._log.warning( 'Invalid process execution time. ' +
                                   'Aborting here ...' )
            self.__proc = self.__vanish_proc( signum = sig.SIGTERM )


    @abstractmethod
    def stop( self ):
        self.__proc = self.__vanish_proc( signum = sig.SIGTERM )
        if self.__proc is not None:
            # trying to kill it.
            self.__proc = self.__vanish_proc( signum = sig.SIGKILL )

        if self.__proc is not None:
            self._log.warning( 'Failed to vanish the sub process.' )


    def __vanish_proc( self, signum = sig.SIGTERM ):
        fn = None
        ret_val = None

        if self.__proc is None:
            self._log.error( 'Process was not created.' )
            return ret_val

        if self.__proc.poll() is not None:
            self._log.info( ( 'Sub process already finished ' +
                              'with return code %d' )
                              % self.__proc.returncode )
            return ret_val

        if signum == sig.SIGTERM:
            fn = self.__proc.terminate
        elif signum == sig.SIGKILL:
            fn = self.__proc.kill
        else:
            self._log.error( 'Abort method not available.' )
            ret_val = self.__proc
            return ret_val

        if fn is not None:
            fn()

        try:
            # timeout value is in seconds [s]
            self.__proc.wait( timeout = 10 )
            if abs( self.__proc.returncode ) != signum:
                self._log.warning( 'Did not get expected ' +
                                   'return code ' +
                                   'after sub process abortion ...' )
        except sp.TimeoutExpired:
            self._log.error( 'Timeout during sub process ' +
                             'abortion. Sub process still going ...' )
            ret_val = self.__proc

        return ret_val



class Recorder( DiffTestComponentBase ):
    def __init__( self, log, cfg ):
        super().__init__( log, cfg )

        self.__sniffers = []
        self.__packets = []
        self.__recording = False

        self.__scapy_cfg()


    @abstractmethod
    def start( self ):
        if self._log.level == logging.DEBUG:
            prn_fn = lambda x: x.summary() \
                if hasattr( x, 'summary' ) \
                else self._log.warning( 'Seems not to be a ' +
                                        'packet object.' )
            be_quiet = False
        else:
            prn_fn = None
            be_quiet = True
        rec_ifs = self._cfg.get_rec_ifs()
        for rec_if in rec_ifs:
            snf = AsyncSniffer(
                count = 0,
                store = 1,
                prn = prn_fn,
                filter = rec_if.get_filter_expr(),
                quiet = be_quiet,
                timeout = None,
                stop_filter = None,
                iface = rec_if.get_if_name(),
                started_callback = None
                )
            self.__sniffers.append( snf )
            snf.start()
            snf = None
        # Give tcpdump a little time to start recording.
        time.sleep( 1 )
        self.__recording = True


    @abstractmethod
    def stop( self ):
        if not self.__recording:
            self._log.info( 'Recording already stopped.' )
            return
        time.sleep( self._cfg.get_pause_before_stop() )
        for sniffer in self.__sniffers:
            pkts = sniffer.stop( join = True )
            self.__packets.append( pkts )
        for ( pkts, rec_if ) in \
            zip( self.__packets, self._cfg.get_rec_ifs() ):
            if_name = rec_if.get_if_name()
            wr_path = rec_if.get_wr_path()
            target_str = rec_if.get_target_str()
            filename = ( wr_path + os.path.sep + if_name + '_' + \
                         target_str + '.pcap' )
            rec_if.set_pcap_path( filename )
            wrpcap( filename, pkts, sync = True )
            os.chmod( filename, 0o666 )
        del self.__packets[ : ]
        del self.__sniffers[ : ]
        self.__recording = False


    # scapy configuration
    def __scapy_cfg( self, socket_layer = 2 ):
        conf.use_pcap = True



class Platform( DiffTestComponentBase ):
    def __init__( self, log, cfg ):
        super().__init__( log, cfg )


    @abstractmethod
    def start( self ):
        self._log.info( 'Starting platform ...' )


    @abstractmethod
    def stop( self ):
        self._log.info( 'Stopping platform ...' )



class Comparator( DiffTestComparatorBase ):
    def __init__( self, log, cfg ):
        super().__init__( log, cfg )
        self.__rptlog = None


    @abstractmethod
    def setup( self, recorder_service ):
        self._cfg = get_initial_cmp_cfg( recorder_service )


    @abstractmethod
    def start( self ):
        self._log.info( 'Starting comparator.' )
        pcap_pairs = self._cfg.get_cmp_pair_pcap_locations()
        rpt_locations = self._cfg.get_cmp_rpt_locations()
        assert( len( pcap_pairs ) == len( rpt_locations ) )
        for ( rpt_loc, pcap_locs ) in zip( rpt_locations, pcap_pairs ):
            self.__rptlog = get_report_logger( rpt_loc,
                also_stdout = True )
            exp_pkts = rdpcap( pcap_locs[ 0 ] )
            act_pkts = rdpcap( pcap_locs[ 1 ] )
            empty = False
            if len( exp_pkts ) == 0:
                self.__rptlog.info( 'Expected packet list is empty.' )
                empty = True
            if len( act_pkts ) == 0:
                self.__rptlog.info( 'Actual packet list is empty.' )
                empty = True
            if empty:
                self.__rptlog.error( 'Not doing any comparison.' )
                log_ascii_fail( self.__rptlog.error )
                return
            if len( exp_pkts ) != len( act_pkts ):
                self.__rptlog.info( 'Expected and actual captures ' +
                    'differ in length. Nevertheless trying to make ' +
                    'a comparison ...' )
            self._cmp( exp_pkts, act_pkts )


    @abstractmethod
    def stop( self ):
        self._log.info( 'Stopping comparator.' )
        if self.__rptlog is not None:
            tear_down_report_logger( self.__rptlog )
            self.__rptlog = None


    def _cmp( self, a, b ):
        # Wireshark packet number starting at 1. :-/
        idx_gen = range( 1, ( len( a ) + 1 ) )
        cmp_res = [ self._eq( idx, c, d ) \
                    for ( idx, c, d ) in zip( idx_gen, a, b ) ]
        time_chk = self.__process_time_ranges( a, b )
        if all( cmp_res ) and time_chk:
            self.__rptlog.info( 'ooooooo All packet comparisons ' +
                'were successful. ooooooo' )
            log_pass( self.__rptlog.info )
        else:
            self.__rptlog.error( 'fffffff Not all packet ' +
                'comparisons were successful. fffffff' )
            log_ascii_fail( self.__rptlog.error )


    def _eq( self, idx, a, b ):
        ret_val = False
        cmp_entries = self._cfg.get_cmp_entries()
        cmp_merge = []
        pkt_mismatch = False
        for entry in cmp_entries:
            scpy_type = entry.get_scapy_type()
            field_get_fns = entry.get_field_getters()
            cmp_fn = entry.get_pkt_cmp_fn()
            if cmp_fn is None:
                cmp_fn = self.__field_cmp_fn
            if scpy_type in a and scpy_type in b:
                cmp = [ cmp_fn( self.__rptlog, idx,
                                x( a[ scpy_type ] ),
                                x( b[ scpy_type ] ) ) \
                    for x in field_get_fns ]
                # list concatenation
                cmp_merge += cmp
            else:
                if scpy_type in a != scpy_type in b:
                    pkt_mismatch = True
                    self.__rptlog.error( str( scpy_type ) +
                        ' is not present in packet a AND packet b.' )
        if all( cmp_merge ) and not pkt_mismatch:
            ret_val = True
        return ret_val


    # This is the default packet compare function
    # which is used if the comparator entry has no
    # specific compare function defined.
    def __field_cmp_fn( self, log, idx, a, b ):
        ret_val = ( a == b )
        if not ret_val:
            exp = str( a )
            act = str( b )
            log.error( ( 'Packet number %4d: ' + \
                         'Expected value: %s, ' + \
                         'actual value: %s' ) % \
                         ( idx, exp, act ) )
        return ret_val


    def __process_time_ranges( self, exp_pkts, act_pkts ):
        time_ranges_gp = self._cfg.get_inter_pkt_times_gp()
        time_ranges_put = self._cfg.get_inter_pkt_times_put()
        descrs = ( 'GP', 'PUT' )
        trs = ( time_ranges_gp, time_ranges_put )
        pkts = ( exp_pkts, act_pkts )
        assert( len( descrs ) == len( trs ) == len( pkts ) )
        results = []
        for ( d, tr, p ) in zip( descrs, trs, pkts ):
            if tr is not None:
                self.__rptlog.info( ( 'Timing ranges to check ' +
                                      'for %s: ' % ( d, ) ) +
                                    str( tr ) )
                res = self.__chk_pkt_times( d, tr, p )
                results.append( res )
            else:
                self.__rptlog.info( ( 'No timing values present ' +
                                      'for target: %s' ) % ( d, ) )
                results.append( True )
        return all( results )


    def __chk_pkt_times( self, d, tr, p ):
        sigma_times = 3
        num_pkt = len( p )
        num_tr = len( tr )
        mult = ( ( num_pkt // num_tr ) + 1 )
        tr_ext = tr * mult
        idx_gen = range( 1, ( len( p ) + 1 ) )
        results = []
        for ( idx, a, b, ( mu, sigma ) ) in \
            zip( idx_gen, p[ 0 : ], p[ 1 : ], tr_ext ):
            diff = float( b.time - a.time )
            self.__rptlog.debug( ( 'Between packet %4d and %4d ' +
                                   '( %s ):' ) % \
                                 ( idx, ( idx + 1 ), d ) )
            self.__rptlog.debug( 'diff : %f s' % diff )
            self.__rptlog.debug( 'mu   : %f s' % mu )
            self.__rptlog.debug( 'sigma: %f s' % sigma )
            left = ( mu - ( sigma_times * sigma ) ) \
                   if ( mu - ( sigma_times * sigma ) ) >= 0.0 \
                   else 0.0
            right = ( mu + ( sigma_times * sigma ) )
            self.__rptlog.debug( ( 'Expected range: ' + \
                                   '[ %f, ..., %f ] s' ) % \
                                   ( left, right ) )
            if diff >= left and diff <= right:
                self.__rptlog.debug( ( 'Inter packet time in range ' + \
                                       'between packet %4d and %4d' ) \
                                       % ( idx, ( idx + 1 ) ) )
                results.append( True )
            else:
                self.__rptlog.error( ( 'Timing violation on %s ' + \
                                       'between packet ' + \
                                       '%4d and %4d' ) % \
                                       ( d, idx, ( idx + 1 ) ) )
                self.__rptlog.error( ( 'Expected range: ' + \
                                       '[ %f, ..., %f ] s' ) % \
                                       ( left, right ) )
                self.__rptlog.error( 'Actual value: %f s' % diff )
                results.append( False )
        self.__rptlog.debug( 'Packet times check: %s' % \
                             ( str( all( results ) ), ) )
        return all( results )



class AggregServiceBundle( DiffTestComponentBase ):
    def __init__( self, log, name_str ):
        super().__init__( log, None )
        self._sub_services = []
        self._targets = {}

        self.__name_str = name_str


    def start( self, target = 'GP' ):
        service = self.__get_service( target )
        service.start()


    def stop( self, target = 'GP' ):
        service = self.__get_service( target )
        service.stop()


    def get_sub_services( self ):
        return self._sub_services


    def _validate( self, bundle_name ):
        self._log.info( 'Installed the %s service.' % bundle_name )


    def _invalidate( self, bundle_name ):
        self.stop()
        self._log.info( 'Uninstalled the %s service.' % bundle_name )


    def _bind_service( self, service, svc_ref ):
        target = svc_ref.get_property( 'target' )
        self._targets[ target ] = service


    def _unbind_service( self, service, svc_ref ):
        target = svc_ref.get_property( 'target' )
        del self._targets[ target ]


    def __get_service( self, target ):
        service = None
        try:
            service = self._targets[ target ]
        except KeyError:
            raise KeyError( ( 'Unknown target device for the ' +
                              '%s service.' ) % self.__name_str )
        return service

