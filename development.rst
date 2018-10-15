.. _deploy_development:

***********
Development
***********

In the :ref:`deploy_quickstart` section we have seen how
to deploy a ``manager`` virtual machine.  You can also deploy
the whole system.  For instance, to deploy a development system
composed of three virtual machines (``manager``, ``as`` and ``ms``),
pass ``discos:development`` to the ``discos-deploy`` script:

.. code-block:: shell

  $ discos-deploy discos:development

This command will connect via SSH to all development machines
and provision the whole system (create users, configure networking,
install yum packages, ACS and its dependencies, utilities, and
eventually the DISCOS dependencies).  To install DISCOS on the deployed
machines, you have two options: you can manually execute the ``discos-get``
command, as we did in the :ref:`deploy_quickstart` section, or you can let
the deplpoyment procedure do it automatically for you by passing the
``--deploy`` argument, followed by the branch you want to deploy, and, in case
you are deploying in a development environment, the ``--station`` argument,
followed by the name of the station, to the ``discos-deploy`` script.

.. code-block:: shell

  $ discos-deploy discos:development --deploy stable --station noto

You can choose a station among ``medicina``, ``noto`` and ``srt``.
This command executes the ``discos-get -s noto stable`` command on
all machines of the system, in parallel.
