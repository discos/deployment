.. _deploy_quickstart:

***********
Quick start
***********

If you have installed the four dependencies, as explained in
section :ref:`dependencies`, then you are ready to download the
`DISCOS deployment repository <https://github.com/discos/deployment.git>`_
and install it:

.. code-block:: shell

   $ git clone https://github.com/discos/deployment.git
   Cloning into 'deployment'...
   $ cd deployment
   $ python setup.py

The last executed command will install some useful scripts that will become
immediately available.
The scripts are:

- :file:`discos-deploy`: a script used to perform the deployment procedure
- :file:`discos-login`: a simple script that performs SSH login to the specified virtual machine
- :file:`discos-vms`: a script used to manage DISCOS virtual machines
- :file:`discos-vnc`: a simple script that opens a VNC viewer to the specified virtual machine


Provision the system
====================
To provision the whole system you just have to execute the
:file:`discos-deploy` command. That is all.
For instance, the following command will create the
``manager`` virtual machine, and will install all
dependencies and configuration files on it:

.. code-block:: shell

   $ discos-deploy manager:development

In this case we give the :file:`discos-deploy` script the ``manager:development``
argument.  It means we want to deploy only the ``manager`` machine, in the
``development`` environment.  We will see more about the environments in
sections :ref:`deploy_development` and :ref:`deploy_production`.

The deployment will take between 30 minutes and one hour, depending of your
machine, because it has to download and install the operating system, all
dependencies (ACS, DISCOS libraries, etc.), create users and groups, configure
the network, and create a complete working environment, as we will see in a moment.

.. note:: You can run the deployment more than once, because the process is
   idempotent, that is, the result of performing the deployment once is
   exactly the same as the result of performing it repeatedly without any
   intervening actions.  In fact, if you run the deployment process once again,
   it will take just a few minutes.

When the deployment is done, we will have the ``manager``
virtual machine delpoyed with everything we need.


Start and stop DISCOS virtual machines
======================================
To start or stop a DISCOS virtual machine, you have to run the
:file:`discos-vms` script specifying a machine and an action.
The machine argument is the name of an already deployed virtual machine,
the action is one among `start` and `stop`.
For instance, if you want to start the ``manager`` machine, all you have to do
is execute the following command:

.. code-block:: shell

    $ discos-vms -m manager start
    Starting machine manager..............done.

As you can see from the example above, the machine name must be preceded by the
``-m`` flag. You can also use the flag ``--machine`` with the same result:

.. code-block:: shell

    $ discos-vms --machine manager start
    Starting machine manager..............done.

As you may have noticed from the previous examples, the ``discos-vms -m <machine> start``
command will block and wait until the machine is booted up and ready.
Executing this command when the selected machine is already powered on will just
print a warning:

.. code-block:: shell

    $ discos-vms -m manager start
    Machine manager is already running.

If you want to stop a running machine you can just execute the same command as
above, but with the ``stop`` action:

.. code-block:: shell

    $ discos-vms -m manager stop
    Powering off machine manager......done.

Just like the ``start`` command, the ``stop`` command will block and wait
until the selected machine has been completely powered off. Trying to stop
a powered off machine will print a warning just like the ``start`` command:

.. code-block:: shell

    $ discos-vms -m manager stop
    Machine manager is not running.


.. note:: Just after the deployment procedure is completed, the
   deployed virtual machine will be already running, so starting it
   with the appropriate command will just output
   ``Machine ... already running``.


Get a DISCOS branch
===================
Use the :file:`discos-login` script to login via ssh to ``manager``:

.. code-block:: shell

    $ discos-login manager
    (branch?) discos@manager ~ $

Currently we have no branch active, that is why there is the ``(branch?)`` text
at the beginning of the prompt.  To get a DISCOS branch and activate it, we have to
use the ``discos-get`` command.  In the following case we get the ``srt-0.1`` branch:

.. figure:: images/discos-get.png
   :figwidth: 100%
   :align: center

Note that this is not a *code-block*, but a screenshot of the shell.  As
you can see, the environment shows the prompt using a syntax highlight.
The ``branch?`` text has been replaced by ``srt-0.1:telescope``, because we
are working on the branch ``srt-0.1``, using its ``telescope`` CDB, that is
the real CDB, hosted in ``SRT/Configuration``.
The ``INTROOT`` has been created inside the ``srt-0.1`` directory.  Here is the
current environment:

.. figure:: images/environment.png
   :figwidth: 100%
   :align: center


Change the CDB
==============
The ``discos-set`` command allows us to specifying the CDB.
We can choose either ``--cdb telescope`` or ``--cdb test``:

.. figure:: images/cdb.png
   :figwidth: 100%
   :align: center

Change the active branch
========================
Sometime we want to have more than one branch and switch between them.
For instance, let's get the ``medicina-0.1`` branch:

.. figure:: images/medicina-0.1.png
   :figwidth: 100%
   :align: center

Now we have two branches, ``srt-0.1`` and ``medicina-0.1``, and the latter is
the active one.  We can switch to the ``srt-0.1`` branch using the ``discos-set``
command:

.. figure:: images/discos-set.png
   :figwidth: 100%
   :align: center


Remove a branch
===============
To remove a branch, just remove the directory:

.. figure:: images/remove-branch.png
   :figwidth: 100%
   :align: center


Get the master branch
=====================
If you want to get a master branch, you need to specify the station:

.. figure:: images/get-master.png
   :figwidth: 100%
   :align: center

What we have seen so far is enough for deploying a small development
environment, but there is more to know.  Maybe you want to deploy the whole
system, composted of several VMs, or maybe you want to deploy the system in
production.  For more information about these topics have a look at the sections
:ref:`deploy_development` and :ref:`deploy_production`.  You will realize that
everything is as easy as we saw here, and for deploying in production is even easier.
