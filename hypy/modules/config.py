"""
Hypy configuration manager module
"""
import configparser
import getpass
from os.path import expanduser

import keyring


CONFIG_FILE_LOCATION = expanduser('~/.hypy.conf')
configuration = None


def load(user: str, passw: str, domain: str, host: str, proto: str):
    """
    Read config file and command line to create the configuration.

    Args:
        user: User passed as command line option.
        passw: Password passed as command line option.
        domain: Domain passed as command line option.
        host: Host passed as command line option.
        proto: Protocol passed as command line option.
    """
    global configuration

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_LOCATION)

        credentials = config['credentials']

        configuration = {'user': credentials['user'],
                         'pass': credentials['pass'],
                         'domain': credentials['domain'],
                         'host': credentials['host']}

        if user is not None:
            configuration['user'] = user
        if passw is not None:
            configuration['pass'] = passw
        if domain is not None:
            configuration['domain'] = domain
        if host is not None:
            configuration['host'] = host

        options = config['options']

        configuration['sync_interval'] = options['sync_interval']
        configuration['protocol'] = options['protocol']
        configuration['ssh_port'] = options['ssh_port']

        if proto is not None:
            configuration['protocol'] = proto

        handle_password(configuration)

    except KeyError:
        print("Please, configure your credentials file - hypy.conf")
        print(CONFIG_FILE_LOCATION)
        exit(1)


def handle_password(configuration):
    """If configuration['pass'] is one of several magic values, replace
    it with a password obtained by prompting or consulting the system
    keyring. Otherwise do nothing.

    The values and how they're handled:
        'prompt': prompt, but do not store in keyring
        'save': prompt and store in keyring
        'load' or absent: load from keyring
    """
    directive = configuration['pass']

    qualified_username = '{user}@{host}.{domain}> '.format(
        user=configuration['user'],
        host=configuration['host'],
        domain=configuration['domain']
    )

    external_password = None
    if directive in ['save', 'prompt']:
        external_password = getpass.getpass("Password for {}".format(qualified_username))
    elif directive == 'load' or not directive:
        external_password = keyring.get_password('hypy', qualified_username)

    if directive == 'save':
        keyring.set_password('hypy', qualified_username, external_password)

    if external_password is not None:
        configuration['pass'] = external_password
