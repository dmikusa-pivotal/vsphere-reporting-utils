# These three functions are borrowed from the pyvmomi examples:
#   https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/tools/cli.py
# code is licensed under apache v2
import argparse
import getpass


def build_arg_parser():
    """
    Builds a standard argument parser with arguments for talking to vCenter

    -h service_host_name_or_ip
    -o optional_port_number
    -u required_user
    -p optional_password
    -S skip ssl validation
    -c cache the output in local json files
    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

    # because -h is reserved for 'help' we use -H for service
    parser.add_argument('-H', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    # because we want -p for password, we use -o for port
    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-S', '--disable_ssl_verification',
                        required=False,
                        action='store_true',
                        help='Disable ssl host certificate verification')

    parser.add_argument('-c', '--cache',
                        default=False,
                        action='store_true',
                        help='Cache results from vSphere')
    return parser


def prompt_for_password(args):
    """
    if no password is specified on the command line, prompt for it
    """
    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args


def get_args():
    """
    Supports the command-line arguments needed to form a connection to vSphere.
    """
    parser = build_arg_parser()
    args = parser.parse_args()
    return prompt_for_password(args)
