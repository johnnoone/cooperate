import argparse
import os
import stat
import sys
from .concurrency import Concurrency
from .modes import *  # noqa
from .nodes import *  # noqa


class CLIParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parse_stdin = True
        self.register('action', 'exec_local', LocalAction)

    def _parse_known_args(self, arg_strings, namespace):
        if self.parse_stdin:
            mode = os.fstat(0).st_mode
            if stat.S_ISFIFO(mode):
                # cat content.txt | cooperate
                for arg_line in sys.stdin.read().splitlines():
                    for arg in self.convert_arg_line_to_args(arg_line):
                        arg_strings.append(arg)
            elif stat.S_ISREG(mode):
                # cooperate < content.txt
                for arg_line in sys.stdin.read().splitlines():
                    for arg in self.convert_arg_line_to_args(arg_line):
                        arg_strings.append(arg)
        return super()._parse_known_args(arg_strings, namespace)

    def convert_arg_line_to_args(self, arg_line):
        if arg_line.startswith('-'):
            return arg_line.split(' ', 1)


class LocalAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 required=False,
                 help=None):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            default=default,
            required=required,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        nodes = getattr(parser, 'nodes', []) or []
        nodes.insert(0, LocalNode())
        setattr(namespace, 'nodes', nodes)


def node_factory(type):
    def wrap(obj):
        if type == 'local':
            return LocalNode()
        if type == 'lxc':
            return LxcNode(obj)
        if type == 'docker':
            return DockerNode(obj)
        if type == 'ssh':
            return SSHNode(obj)
        raise argparse.ArgumentTypeError('Bad type %r for %r' % (type, obj))
    return wrap


def mode_factory(type):
    if type == 'all':
        return AllMode
    elif type == 'distribute':
        return DistibuteMode
    else:
        raise argparse.ArgumentTypeError('Bad mode %r' % type)


def batch_factory(value):
    try:
        value = int(value, 10)
        return Concurrency(size=value)
    except ValueError:
        pass
    if value.endswith('%'):
        try:
            value = int(value[:-1], 10)
            if (0 < value) and (value < 100):
                return Concurrency(part=value)
        except ValueError:
            pass
    raise argparse.ArgumentTypeError('Bad value %r' % value)


def env_factory(value):
    if '=' not in value:
        raise argparse.ArgumentTypeError('Bad value %r' % value)
    a, b, c = value.partition('=')
    return (a, c)


def get_parser(args=None):

    ns = argparse.Namespace()

    args = args or sys.argv[1:]
    if '--' in args:
        # every nodes must exec this only command
        pos = args.index('--')
        args, command = args[:pos], args[pos+1:]
        setattr(ns, 'commands', [command])
        setattr(ns, 'mode', AllMode)

    parser = CLIParser(description='execute commands in a cooperative manner, by distributing them to many nodes', fromfile_prefix_chars='@')  # noqa
    nodes_loader(parser)

    if not hasattr(ns, 'execute'):
        parser.add_argument('-c', '--command',
                            action='append',
                            metavar='COMMAND',
                            dest='commands',
                            help='command to execute. repeatable. one required')  # noqa
    if not hasattr(ns, 'mode'):
        parser.add_argument('-m', '--mode',
                            type=mode_factory,
                            default='all',
                            help='select a mode (all, distribute)')
    parser.add_argument('-b', '--batch',
                        type=batch_factory,
                        metavar='SIZE',
                        help='how many jobs must be executed concurrently')
    parser.add_argument('-e', '--env',
                        type=env_factory,
                        action='append',
                        metavar='ENV',
                        dest='env',
                        help='set environment variable')
    parser.add_argument('-t', '--timeout',
                        type=int,
                        metavar='SECONDS',
                        help='restrict the whole execution time')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s 0.2')

    return parser, ns, args


def nodes_loader(parser):
    group = parser.add_argument_group('nodes',
                                      description='distribute commands to these nodes. repeatable. one required')  # noqa
    group.add_argument('-l', '--local',
                       action='exec_local',
                       help='execute locally')
    group.add_argument('--docker',
                       action='append',
                       type=node_factory('docker'),
                       metavar='CONTAINER',
                       dest='nodes',
                       help='execute in a local container')
    group.add_argument('--lxc',
                       action='append',
                       type=node_factory('lxc'),
                       metavar='CONTAINER',
                       dest='nodes',
                       help='execute in a local container')
    group.add_argument('--ssh',
                       action='append',
                       type=node_factory('ssh'),
                       metavar='ACCESS',
                       dest='nodes',
                       help='execute in a remote server via ssh')
    return parser
