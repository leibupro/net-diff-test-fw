
import os
import sys

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


def install_bundles( context, bundles ):
    for bundle in bundles:
        context.install_bundle( bundle ).start()
    return context


def run_test_case( context, tc_bundle ):
    ref_config = context.get_service_reference( tc_bundle )

    with use_service( context, ref_config ) as svc_config:
        # Here, svc_config points to test case bundle.
        svc_config.run()


def install_bundles_tc_icmp_0( context ):
    bundles = [ 'generator_ping_GP', 'generator_ping_PUT', \
                'recorder_ping_GP', 'recorder_ping_PUT', \
                'generator_icmp_0', 'recorder_icmp_0', \
                'comparator_icmp_0', \
                'test_icmp_0' ]
    context = install_bundles( context, bundles )
    return context


def install_bundles_tc_tlshs( context ):
    bundles = [ 'generator_tlshs_GP', 'generator_tlshs_PUT', \
                'recorder_tlshs_GP', 'recorder_tlshs_PUT', \
                'generator_tlshs', 'recorder_tlshs', \
                'comparator_tlshs', \
                'test_tlshs' ]
    context = install_bundles( context, bundles )
    return context


def run_tc_icmp_0( context ):
    log.info( 'Testing the ICMP 0 test case service.' )
    run_test_case( context, 'test_icmp_0' )


def run_tc_tlshs( context ):
    log.info( 'Testing the TLS handshake test case service.' )
    run_test_case( context, 'test_tlshs' )


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

    context = install_bundles_tc_icmp_0( context )
    context = install_bundles_tc_tlshs( context )
    run_tc_icmp_0( context )
    run_tc_tlshs( context )

    if framework.stop():
        log.info( 'Framework sucessfully stopped. This is the end.' )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as ki:
        print( str( ki ) )
        signal_handler()

