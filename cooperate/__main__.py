import asyncio
import asyncio.subprocess
import signal
import functools
from .cli import get_parser
from .renderers import StatusRenderer  # noqa
from aioutils import Group, Pool


def broadcast(args):
    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, loop, signame))

    env = dict(args.env or [])
    renderer = StatusRenderer()

    def printer(future, node, command):
        data = renderer.render(future, node, command)
        print(data)

    nodes = args.nodes or []

    jobs = args.mode(nodes, args.commands)
    if args.batch:
        pooler = Pool(args.batch.batch(jobs))
    else:
        pooler = Group()

    for node, command in jobs:
        task = pooler.spawn(node.run(command, env=env))
        render = functools.partial(printer, node=node, command=command)
        task.add_done_callback(render)
    pooler.join()

    loop.close()


def ask_exit(loop, signame):
    print("# got signal %s: exit" % signame)
    loop.stop()


def run():
    parser, ns, remains = get_parser()
    args = parser.parse_args(remains, namespace=ns)
    broadcast(args)


if __name__ == '__main__':
    run()
