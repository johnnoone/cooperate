Cooperate
=========

**cooperate** is a shell command that execute commands in a cooperative manner, by distributing them to many nodes.

It requires Python >= 3.3 and asyncio.


For example::

    cooperate --local -- echo FOO

Will execute the job "echo FOO" locally.

This one::

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


Installation
------------

::

    pip install cooperate

Nodes
-----

Commands can be distribued thru these kind of nodes:

* **--local** execute locally
* **--ssh** execute thru ssh
* **--docker** execute in a local docker container
* **--lxc** execute in a local lxc container

These options can be repeated as often as needed.

Modes
-----

By default, it spawns every commands to every nodes.

The **-m**, **--mode** allow to configure the desired mode.

The **all** mode executes all commands in all nodes::

    cooperate --local --ssh me@my.node --ssh me@my.second.node \
        --command="echo FOO" --command="echo BAR"

Is equivalent to::

    echo FOO
    echo BAR
    ssh me@my.second.node echo FOO
    ssh me@my.second.node echo BAR


The **distribute** mode share the commands out among all the nodes::

    cooperate --local --ssh me@my.node --ssh me@my.second.node \
        --command="echo FOO" --command="echo BAR" --mode=distribute

Is equivalent to::

    echo FOO
    ssh me@my.second.node echo BAR


Concurrency
-----------

By default, it executes all jobs simultaneously.

The **-b**, **--batch** option allows to execute on only a specify number of jobs at a time. Both percentages and finite numbers are supported::

    cooperate --local --concurrence 1 \
        --command="echo FOO" --command="echo BAR" --command="echo BAZ"

    cooperate --local --concurrence 33% \
        --command="echo FOO" --command="echo BAR" --command="echo BAZ"

The concurrency system maintains a window of running jobs. When a job returns then it starts a remnant job and so on.


Feeding ``cooperate``
---------------------

Arguments can accept multiple input files for providing arguments, for example::

    cat arguments.txt | cooperate
    cooperate < arguments.txt
    cooperate @arguments1.txt @arguments2.txt

These files must have a line per argument, like this::

    --command echo $FOO
    --local
    --ssh server1
    --ssh server2


Ouputing
--------

``cooperate`` will output to the stdout each result as they come in single YAML documents, with these keys

:code: the return code
:command: the executed command
:error: error occured into cooperate, if any
:node: the node name
:stderr: stderr of the command, if any
:stdout: stdout of the command, if any
