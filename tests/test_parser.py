from cooperate.cli import get_parser, broadcast
import pytest
import shlex


@pytest.mark.parametrize('input, expected', [
    ('--command="echo FOO"', {'commands': ['echo FOO']}),
    ('--command="echo FOO BAR"', {'commands': ['echo FOO BAR']}),
    ('--command="echo \\"FOO BAR\\""', {'commands': ['echo "FOO BAR"']}),
    ('-- echo FOO', {'execute': ['echo', 'FOO'], 'action': 'all'}),
    ('--ssh=root@localhost -- echo FOO', {'execute': ['echo', 'FOO'],
                                          'action': 'all',
                                          'ssh': ['root@localhost']}),
    ('--local --command="echo FOO"', {'commands': ['echo FOO'], 'local': True}),
    ('--local -- echo FOO', {'execute': ['echo', 'FOO'], 'action': 'all', 'local': True}),
])
def test_eval(input, expected):
    argv = shlex.split(input)
    parser, ns, argv = get_parser(argv)
    args = parser.parse_args(argv, namespace=ns)

    comform = lambda x: {k: v for k, v in x.items() if v}
    expected = comform(expected)
    real = comform(args.__dict__)
    assert expected == real


@pytest.mark.parametrize('input', [
    '--local -- echo FOO',
])
def test_run(input):
    parser = get_parser()
    args = parser.parse_args(shlex.split(input))
    broadcast(args)
