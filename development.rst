.. _deploy_development:

***********
Development
***********

In the :ref:`deploy_quickstart` section we have seen how
to deploy a ``manager`` virtual machine.  You can also deploy
the whole system.  For instance, to deploy a development system
composed of three virtual machines (``manager``, ``as`` and ``ms``),
pass ``large:development`` to the ``build`` script:

.. code-block:: shell

  $ ./build large:development

This command will connect via SSH to all development machines
and provision the whole system (create users, configure networking,
install yum packages, ACS and its dependencies, utilities, and
eventually the DISCOS dependencies).  To get a particular
DISCOS branch you have two options: you can manually execute
the ``get-discos`` command, as we did in the :ref:`deploy_quickstart`
section, or you can do it by executing another time the ``build`` script.
This time you have to use the ``--deploy`` argument:

.. code-block:: shell

  $ ./build large:development --deploy srt-0.1

This command executes the ``discos-get srt-0.1`` command on all
machines of the system, in parallel.
