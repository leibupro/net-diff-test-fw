
from difftest.bases import Recorder
from difftest.util import get_logger
from difftest.testenv import get_gp_rec_cfg, \
                             inject_tlshs_rec_cmd


# iPOPO decorators
from pelix.ipopo.decorators import \
    ComponentFactory, Property, Provides, \
    Validate, Invalidate, Instantiate


# Name the iPOPO component factory
@ComponentFactory( 'recorder_tlshs_gp_factory' )
# This component provides a generator service
@Provides( 'recorder_tlshs_base_service' )
# It is the ping generator towards the golden platform
@Property( '_target', 'target', 'GP' )
# Automatically instantiate a component when this factory is loaded
@Instantiate( 'recorder_tlshs_gp_instance' )
class TlsHsRecorderImplGP( Recorder ):
    def __init__( self ):
        rec_cfg = get_gp_rec_cfg()
        rec_cfg = inject_tlshs_rec_cmd( rec_cfg )
        log = get_logger( logger_name = __name__ )
        super().__init__( log, rec_cfg )


    @Validate
    def validate( self, context ):
        self._log.info( 'Installed the %s service.' % __name__ )


    @Invalidate
    def invalidate( self, context ):
        self.stop()
        self._log.info( 'Uninstalled the %s service.' % __name__ )


    def start( self ):
        super().start()


    def stop( self ):
        super().stop()

