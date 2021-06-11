
from difftest.bases import TestCaseBase
from difftest.util import get_logger


# iPOPO decorators
from pelix.ipopo.decorators import \
    ComponentFactory, Property, Provides, Requires, \
    Validate, Invalidate, Instantiate, \
    BindField, UnbindField


# Name the iPOPO component factory
@ComponentFactory( 'test_icmp_0_factory' )
# This component proviedes the ICMP 0 test case
@Provides( 'test_icmp_0' )
@Requires( '_gen_service', 'generator_icmp_0_service' )
@Requires( '_rec_service', 'recorder_icmp_0_service' )
@Requires( '_cmp_service', 'comparator_icmp_0_service' )
# Automatically instantiate a component when this factory is loaded
@Instantiate( 'test_icmp_0_instance' )
class TestIcmp0( TestCaseBase ):
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

