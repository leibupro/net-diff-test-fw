
from difftest.bases import Generator
from difftest.util import get_logger
from difftest.testenv import get_put_cfg, \
                             get_put_gen_cfg, \
                             inject_tlshs_gen_cmd

# iPOPO decorators
from pelix.ipopo.decorators import \
    ComponentFactory, Property, Provides, \
    Validate, Invalidate, Instantiate


# Name the iPOPO component factory
@ComponentFactory( 'generator_tlshs_put_factory' )
# This component provides a generator service
@Provides( 'generator_tlshs_base_service' )
# It is the ping generator towards the golden platform
@Property( '_target', 'target', 'PUT' )
# Automatically instantiate a component when this factory is loaded
@Instantiate( 'generator_tlshs_put_instance' )
class TlsHsGeneratorImplPUT( Generator ):
    def __init__( self ):
        platf_cfg = get_put_cfg()
        gen_cfg = get_put_gen_cfg( platf_cfg )
        gen_cfg = inject_tlshs_gen_cmd( gen_cfg )
        log = get_logger( logger_name = __name__ )
        super().__init__( log, gen_cfg )


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

