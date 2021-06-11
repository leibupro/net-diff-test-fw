
from difftest.bases import Comparator
from difftest.cfg import ComparatorEntry
from difftest.util import get_logger
from difftest.testenv import inject_icmp_cmd_0_trs


# iPOPO decorators
from pelix.ipopo.decorators import \
    ComponentFactory, Property, Provides, \
    Validate, Invalidate, Instantiate


# Name the iPOPO component factory
@ComponentFactory( 'comparator_icmp_0_factory' )
# This component provides a comparator service
@Provides( 'comparator_icmp_0_service' )
# Automatically instantiate a component when this factory is loaded
@Instantiate( 'comparator_icmp_0_instance' )
class ComparatorIcmp( Comparator ):
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


    # Would be an individual packet compare function ...
    def compare_fn( self, log, idx, a, b ):
        log.warning( 'Foo Bar ... %d' % idx )
        return True


    def enrich_cmp_cfg( self ):
        if super().enrich_cmp_cfg():
            from scapy.all import IP, ICMP
            CE = ComparatorEntry
            cmp_entries = [
                CE( IP, ( lambda x: x.version, ),
                          pkt_cmp_fn = None ),
                CE( ICMP, ( lambda x: x.type,
                            lambda x: x.code,
                            lambda x: x.seq ),
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
        self._cfg = inject_icmp_cmd_0_trs( self._cfg )


    def start( self ):
        super().start()


    def stop( self ):
        super().stop()

