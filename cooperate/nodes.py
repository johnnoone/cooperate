import asyncio
import shlex

__all__ = ['Node', 'DockerNode', 'LocalNode', 'LxcNode', 'SSHNode']


def format_env(env):
    return ['%s=%s' % (k, shlex.quote(v)) for k, v in env.items()]


def loop_env(env):
    for k, v in env.items():
        yield '%s=%s' % (k, shlex.quote(v))


def prepare_cmd(command, env=None):
    args = []
    join = False
    if env:
        args.append('env')
        args.extend(loop_env(env))
    if isinstance(command, (list, tuple)):
        args.extend(command)
    else:
        args.append(command)
        join = True

    if join:
        return ' '.join(args)
    return args


class Result:

    def __init__(self, code=None, stdout=None, stderr=None, error=None):
        self.code = code
        self.stdout = stdout
        self.stderr = stderr
        self.error = error

    @property
    def succeeded(self):
        return self.code == 0 or not self.error

    def __repr__(self):
        return '<Result(code=%s, stdout...)>' % self.code


class Node:

    @asyncio.coroutine
    def run(self, command, env=None):
        raise NotImplementedError()


class DockerNode(Node):

    def __init__(self, container):
        self.container = container

    @property
    def name(self):
        return '%s' % self.container

    @asyncio.coroutine
    def run(self, command, env=None):
        kwargs = {'stdout': asyncio.subprocess.PIPE,
                  'stderr': asyncio.subprocess.PIPE}
        if isinstance(command, (list, tuple)):
            args = ['docker', 'exec', self.container]
            if env:
                args.append('env')
                args.extend(format_env(env))
            args.extend(command)
            create = asyncio.create_subprocess_exec(*args, **kwargs)
        else:
            if env:
                command = 'env %s %s' % (' '.join(format_env(env)), command)
            cmd = 'docker exec %s %s' % (self.container, command)
            create = asyncio.create_subprocess_shell(cmd, **kwargs)
        proc = yield from create
        stdout, stderr = yield from proc.communicate()
        return Result(proc.returncode,
                      stdout=stdout.decode('utf-8').rstrip('\r\n'),
                      stderr=stderr.decode('utf-8').rstrip('\r\n'))


class LocalNode(Node):

    @property
    def name(self):
        return 'local'

    @asyncio.coroutine
    def run(self, command, env=None):
        args = {'stdout': asyncio.subprocess.PIPE,
                'stderr': asyncio.subprocess.PIPE,
                'env': env}
        if isinstance(command, (list, tuple)):
            create = asyncio.create_subprocess_exec(*command, **args)
        else:
            create = asyncio.create_subprocess_shell(command, **args)
        proc = yield from create
        stdout, stderr = yield from proc.communicate()
        return Result(proc.returncode,
                      stdout=stdout.decode('utf-8').rstrip('\r\n'),
                      stderr=stderr.decode('utf-8').rstrip('\r\n'))


class LxcNode(Node):

    def __init__(self, container):
        self.container = container

    @property
    def name(self):
        return '%s' % self.container

    @asyncio.coroutine
    def run(self, command, env=None):
        args = {'stdout': asyncio.subprocess.PIPE,
                'stderr': asyncio.subprocess.PIPE}
        if isinstance(command, (list, tuple)):
            args = ['lxc-attach', '--name', self.container, '--']
            if env:
                args.extend(format_env(env))
            args.extend(command)
            create = asyncio.create_subprocess_exec(*args, **args)
        else:
            if env:
                command = 'env %s %s' % (' '.join(format_env(env)), command)
            cmd = 'lxc-attach --name %s -- %s' % (self.container, command)
            create = asyncio.create_subprocess_shell(cmd, **args)
        proc = yield from create
        stdout, stderr = yield from proc.communicate()
        return Result(proc.returncode,
                      stdout=stdout.decode('utf-8').rstrip('\r\n'),
                      stderr=stderr.decode('utf-8').rstrip('\r\n'))


class SSHNode(Node):

    def __init__(self, connect):
        self.connect = connect

    @property
    def name(self):
        return '%s' % self.connect

    @asyncio.coroutine
    def run(self, command, env=None):
        options = {
            'stdout': asyncio.subprocess.PIPE,
            'stderr': asyncio.subprocess.PIPE}
        args = ['ssh', self.connect]

        args = []
        if env:
            args.append('env')
            args.extend(format_env(env))
        if not isinstance(command, (list, tuple)):
            args = shlex.split(command)
        args.extend(command)

        cmd = 'ssh %s %s' % (self.connect, shlex.quote(' '.join(args)))

        create = asyncio.create_subprocess_shell(cmd,  **options)
        proc = yield from create
        stdout, stderr = yield from proc.communicate()
        return Result(proc.returncode,
                      stdout=stdout.decode('utf-8').rstrip('\r\n'),
                      stderr=stderr.decode('utf-8').rstrip('\r\n'))
