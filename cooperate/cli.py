import argparse
import asyncio
import asyncio.subprocess
import functools
import os.path
import signal
import sys
from .modes import *
from .nodes import *
from .renderers import *

here = os.path.dirname(os.path.abspath(__file__))

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
        else:
            raise argparse.ArgumentTypeError('Bad type %r for %r' % (type, obj))
    return wrap


def mode_factory(type):
    if type == 'all':
        return AllMode
    elif type == 'distribute':
        return DistibuteMode
    else:
        raise argparse.ArgumentTypeError('Bad mode %r' % type)


def get_parser(args=None):

    ns = argparse.Namespace()

    args = args or sys.argv[1:]
    if '--' in args:
        # every nodes must exec this only command
        pos = args.index('--')
        args, command = args[:pos], args[pos+1:]
        setattr(ns, 'commands', [command])
        setattr(ns, 'mode', AllMode)

    parser = argparse.ArgumentParser()
    if not hasattr(ns, 'execute'):
        parser.add_argument('--command',
                            action='append',
                            dest='commands',
                            help='command to execute')
    if not hasattr(ns, 'mode'):
        parser.add_argument('--mode',
                            type=mode_factory,
                            default='all',
                            help='which mode?')
    parser.add_argument('--local',
                        action='store_true',
                        dest='local',
                        help='execute locally')
    parser.add_argument('--docker',
                        action='append',
                        type=node_factory('docker'),
                        dest='nodes',
                        help='execute in a local container')
    parser.add_argument('--lxc',
                        action='append',
                        type=node_factory('lxc'),
                        dest='nodes',
                        help='execute in a local container')
    parser.add_argument('--ssh',
                        action='append',
                        type=node_factory('ssh'),
                        dest='nodes',
                        help='execute in a remote server via ssh')
    parser.add_argument('--timeout',
                        type=int,
                        help='add a timeout to the global execution time')

    return parser, ns, args


def broadcast(args):

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, loop, signame))

    renderer = StatusRenderer()

    nodes = args.nodes or []
    if args.local:
        nodes.insert(0, LocalNode())

    tasks = []
    for node, command in args.mode(nodes, args.commands):
        task = asyncio.async(node.run(command))
        render = functools.partial(renderer.render, node=node, command=command)
        task.add_done_callback(render)
        tasks.append(task)

    loop.run_until_complete(asyncio.wait(tasks, timeout=args.timeout))
    loop.close()


def ask_exit(loop, signame):
    print("got signal %s: exit" % signame)
    loop.stop()


def main():
    parser, ns, remains = get_parser()
    args = parser.parse_args(remains, namespace=ns)
    broadcast(args)


if __name__ == '__main__':
    main()
