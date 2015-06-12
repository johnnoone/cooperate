Cooperate
=========

**cooperate** is a shell command that execute commands in a cooperative manner, by distributing them to many nodes.

It requires Python >= 3.3 and asyncio.


For example::

    cooperate --local -- echo FOO

Will execute the command "echo FOO" locally::

    cooperate --ssh me@my.node -- echo FOO

Is barelly equivalent to::

    ssh me@my.node echo FOO

You can declare as many nodes as you want, for example::

    cooperate --local --ssh me@my.node --ssh me@my.second.node -- echo FOO

Is equivalent to::

    echo FOO
    ssh me@my.node echo FOO
    ssh me@my.second.node echo FOO

You can also declare many commands at once::

    cooperate --local --command "echo FOO" --command "echo BAR"

Is equivalent to::

    echo FOO
    echo BAR


Nodes
-----

Commands can be distribued thru these kind of nodes:

    * **local** execute locally
    * **ssh** execute thru ssh
    * **docker** execute in a local docker container
    * **lxc** execute in a local lxc container


Modes
-----

There is 2 modes: **all** and **distribute**.
By default, it will use the 'all' mode, which execute all commands in all nodes::

    cooperate --local --ssh me@my.node --ssh me@my.second.node \
        --command="echo FOO" --command="echo BAR"

Is equivalent to::

    echo FOO
    echo BAR
    ssh me@my.second.node echo FOO
    ssh me@my.second.node echo BAR


You can also 'distribute' commands between all nodes::

    cooperate --local --ssh me@my.node --ssh me@my.second.node \
        --command="echo FOO" --command="echo BAR" --mode=distribute

Is equivalent to::

    echo FOO
    ssh me@my.second.node echo BAR
