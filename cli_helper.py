import argparse
import getpass


class ArgBuilder:
    """
    Builds a standard argument parser with arguments for talking to vCenter

    -h service_host_name_or_ip
    -o optional_port_number
    -u required_user
    -p optional_password
    -S skip ssl validation
    -c cache the output in local json files
    """
    def __init__(self):
        self.args = None
        self.parser = argparse.ArgumentParser(
            description='Standard Arguments for talking to vCenter')

        # because -h is reserved for 'help' we use -H for service
        self.parser.add_argument(
            '-H', '--host',
            required=True,
            action='store',
            help='vSphere service to connect to')

        # because we want -p for password, we use -o for port
        self.parser.add_argument(
            '-o', '--port',
            type=int,
            default=443,
            action='store',
            help='Port to connect on')

        self.parser.add_argument(
            '-u', '--user',
            required=True,
            action='store',
            help='User name to use when connecting to host')

        self.parser.add_argument(
            '-p', '--password',
            required=False,
            action='store',
            help='Password to use when connecting to host')

        self.parser.add_argument(
            '-S', '--disable_ssl_verification',
            required=False,
            action='store_true',
            help='Disable ssl host certificate verification')

        self.parser.add_argument(
            '-c', '--cache',
            default=False,
            action='store_true',
            help='Cache results from vSphere')

    def prompt_for_password(self):
        """
        if no password is specified on the command line, prompt for it
        """
        if not self.args.password:
            self.args.password = getpass.getpass(
                prompt='Enter password for host %s and user %s: ' %
                       (self.args.host, self.args.user))
        return self.args

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def process_args(self):
        """
        Supports the command-line arguments needed to form a connection
        to vSphere.
        """
        self.args = self.parser.parse_args()
        return self.prompt_for_password()
