
from difftest.bases import TestCaseBase
from difftest.util import get_logger


# iPOPO decorators
from pelix.ipopo.decorators import \
    ComponentFactory, Property, Provides, Requires, \
    Validate, Invalidate, Instantiate, \
    BindField, UnbindField


# Name the iPOPO component factory
@ComponentFactory( 'test_tlshs_factory' )
# This component proviedes the TLS handshake test case
@Provides( 'test_tlshs' )
@Requires( '_gen_service', 'generator_tlshs_service' )
@Requires( '_rec_service', 'recorder_tlshs_service' )
@Requires( '_cmp_service', 'comparator_tlshs_service' )
# Automatically instantiate a component when this factory is loaded
@Instantiate( 'test_tlshs_instance' )
class TestTlsHs( TestCaseBase ):
    def __init__( self ):
        log = get_logger( logger_name = __name__ )
        super().__init__( log )


    @Validate
    def validate( self, context ):
        self._log.info( 'Installed the %s case.' % __name__ )


    @Invalidate
    def invalidate( self, context ):
        self.unrun()
        self._log.info( 'Uninstalled the %s case.' % __name__ )


    def run( self, bundle_name = __name__ ):
        super().run( bundle_name = bundle_name )


    def unrun( self, bundle_name = __name__ ):
        super().unrun( bundle_name = bundle_name )

