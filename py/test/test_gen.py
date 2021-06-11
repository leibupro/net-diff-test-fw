
import os
import sys
import time
import multiprocessing as mp

# Pelix framework module and utility methods
import pelix.framework
from pelix.utilities import use_service

from difftest.util import get_logger

log = get_logger( logger_name = __name__ )
framework = None


def signal_handler():
    print( 'Process received SIGINT. Exiting ...' )
    if framework is not None:
        framework.stop()
    sys.exit( os.EX_OK )


def main():
    global framework
    framework = pelix.framework.create_framework( (
        # iPOPO
        'pelix.ipopo.core',
        # Shell core (engine)
        'pelix.shell.core' ) )

    # Start the framework, and the pre-installed bundles
    framework.start()

    # Get the bundle context of the framework, i.e. the link between
    # the framework starter and its content.
    context = framework.get_bundle_context()

    # Start the generator bundles, provide the specific generators.
    context.install_bundle( 'generator_ping_GP' ).start()
    context.install_bundle( 'generator_ping_PUT' ).start()

    # Start the ICMP generator, this service requires the ping
    # generators towards the specific target platforms.
    context.install_bundle( 'generator_icmp_0' ).start()

    ref_config = context.get_service_reference(
        'generator_icmp_0_service' )
    with use_service( context, ref_config ) as svc_config:
        # Here, svc_config points to the generator service
        log.info( 'Testing the ICMP generator service.' )
        svc_config.start( target = 'GP' )
        svc_config.start( target = 'PUT' )

    if framework.stop():
        log.info( 'Framework sucessfully stopped. This is the end.' )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as ki:
        print( str( ki ) )
        signal_handler()

