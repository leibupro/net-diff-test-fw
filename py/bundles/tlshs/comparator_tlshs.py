
from difftest.bases import Comparator
from difftest.cfg import ComparatorEntry
from difftest.util import get_logger
from difftest.testenv import inject_tlshs_trs


# iPOPO decorators
from pelix.ipopo.decorators import \
    ComponentFactory, Property, Provides, \
    Validate, Invalidate, Instantiate

from scapy.all import load_layer
load_layer( 'tls' )


# Name the iPOPO component factory
@ComponentFactory( 'comparator_tlshs_factory' )
# This component provides a comparator service
@Provides( 'comparator_tlshs_service' )
# Automatically instantiate a component when this factory is loaded
@Instantiate( 'comparator_tlshs_instance' )
class ComparatorTlsHs( Comparator ):
    def __init__( self ):
        log = get_logger( logger_name = __name__ )
        super().__init__( log, None )


    @Validate
    def validate( self, context ):
        self._log.info( 'Installed the %s service.' % __name__ )


    @Invalidate
    def invalidate( self, context ):
        self.stop()
        self._log.info( 'Uninstalled the %s service.' % __name__ )


    # We have to pre-load the packets with the TLS
    # layer of scapy. Therefore we override the _eq
    # function and call the parent class method again.
    def _eq( self, idx, a, b ):
        ret_val = False
        try:
            a = TLS( a.load )
            b = TLS( b.load )
        except ( TypeError, KeyError, AttributeError ) as e:
            self._log.error( str( e ) )
        ret_val = super()._eq( idx, a, b )
        return ret_val


    def enrich_cmp_cfg( self ):
        if super().enrich_cmp_cfg():
            CE = ComparatorEntry
            cmp_entries = [
                CE( TLSClientHello, ( lambda x: x.ciphers, ),
                    pkt_cmp_fn = None ),
                CE( TLSServerHello, ( lambda x: x.cipher, ),
                    pkt_cmp_fn = None )
            ]
            for ce in cmp_entries:
                self._cfg.add_cmp_entry( ce )
            return True
        else:
            return False


    def setup( self, recorder_service ):
        super().setup( recorder_service )
        self.enrich_cmp_cfg()
        self._cfg = inject_tlshs_trs( self._cfg )


    def start( self ):
        super().start()


    def stop( self ):
        super().stop()

