
from difftest.util import get_logger
from difftest.bases import AggregServiceBundle


# iPOPO decorators
from pelix.ipopo.decorators import \
    ComponentFactory, Property, Provides, Requires, \
    Validate, Invalidate, Instantiate, \
    BindField, UnbindField


# Name the iPOPO component factory
@ComponentFactory( 'recorder_tlshs_factory' )
# This component provides a generator service
@Provides( 'recorder_tlshs_service' )
# Consume all ping generator services available (aggregate them)
@Requires( '_sub_services', 'recorder_tlshs_base_service',
           aggregate = True )
# Automatically instantiate a component when this factory is loaded
@Instantiate( 'recorder_tlshs_instance' )
class RecorderTlsHs( AggregServiceBundle ):
    def __init__( self ):
        log = get_logger( logger_name = __name__ )
        super().__init__( log, 'TLS handshake' )


    @BindField( '_sub_services' )
    def bind_ping_gen( self, field, service, svc_ref ):
        self._bind_service( service, svc_ref )


    @UnbindField( '_sub_services' )
    def unbind_ping_gen( self, field, service, svc_ref ):
        self._unbind_service( service, svc_ref )


    @Validate
    def validate( self, context ):
        self._validate( __name__ )


    @Invalidate
    def invalidate( self, context ):
        self._invalidate( __name__ )

