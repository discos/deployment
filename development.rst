.. _deploy_development:

***********
Development
***********

In the :ref:`deploy_quickstart` section we have seen how
to deploy a ``manager`` virtual machine.  You can also deploy
the whole system.  For instance, to deploy a development system
composed of three virtual machines (``manager``, ``as`` and ``ms``),
pass ``discos:development`` to the ``build`` script:

.. code-block:: shell

  $ ./build discos:development

This command will connect via SSH to all development machines
and provision the whole system (create users, configure networking,
install yum packages, ACS and its dependencies, utilities, and
eventually the DISCOS dependencies).  To get a particular
DISCOS branch you have two options: you can manually execute
the ``discos-get`` command, as we did in the :ref:`deploy_quickstart`
section, or you can do it by passing the ``--deploy`` argument,
followed by the branch you want to deploy, and, in the case of
development environment, the ``--station`` argument, followed
by the name of the station, to the ``build`` script.

.. code-block:: shell

  $ ./build discos:development --deploy latest64 --station medicina

You can choose a station among ``medicina``, ``noto`` and ``srt``.
This command executes the ``discos-get latest64 -s medicina`` command on
all machines of the system, in parallel.
