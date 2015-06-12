Cooperate
=========

**cooperate** is a shell command that execute commands in a cooperative manner, by distributing them to many nodes.

It requires Python >= 3.3 and asyncio.


For example::

    cooperate --local -- echo FOO

Will execute the job "echo FOO" locally::

    cooperate --ssh me@my.node -- echo FOO

Is barelly equivalent to::

    ssh me@my.node echo FOO

You can declare as many nodes as you want. For example::

    cooperate --local --ssh me@my.node --ssh me@my.second.node -- echo FOO

Is equivalent to::

    echo FOO
    ssh me@my.node echo FOO
    ssh me@my.second.node echo FOO

You can also declare many jobs at once. For example::

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


You can also **distribute** commands between all nodes::

    cooperate --local --ssh me@my.node --ssh me@my.second.node \
        --command="echo FOO" --command="echo BAR" --mode=distribute

Is equivalent to::

    echo FOO
    ssh me@my.second.node echo BAR


Concurrency
-----------

By default, it will execute all jobs simultaneously.
It can be set by a **--concurrence** parameter, where expected values are a number

The **--concurrence** option allows to execute on only a specify number of jobs at a time. Both percentages and finite numbers are supported::

    cooperate --local --concurrence 1 \
        --command="echo FOO" --command="echo BAR" --command="echo BAZ"

    cooperate --local --concurrence 33% \
        --command="echo FOO" --command="echo BAR" --command="echo BAZ"

The concurrency system maintains a window of running jobs. When a job returns then it starts a remnant job and so on.
