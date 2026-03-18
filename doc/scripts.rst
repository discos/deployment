.. _deploy_scripts:

**************
Useful scripts
**************

If you installed the `deployment` Python package as described in the
:ref:`deploy_quickstart` section, you will have access to the following
command line tools:

- :file:`discos-container`: manage the Docker-based development environment
- :file:`discos-vms`: manage DISCOS virtual machines (legacy support)
- :file:`discos-login`: perform SSH login to a deployed machine
- :file:`discos-vnc`: open a VNC session to a deployed machine


Manage the development container, ``discos-container``
======================================================

The :file:`discos-container` script is used to manage the Docker-based
development environment.

Command syntax
--------------

::

   discos-container [-v] <command> [options]

Available commands are:

- ``build``
- ``remove``
- ``load <imgfile>``
- ``save <imgfile>``
- ``status``
- ``start``
- ``stop``
- ``restart``
- ``create``
- ``destroy``

The ``-v`` or ``--verbose`` option enables Docker output.


Build or remove images
----------------------

To build the base image:

.. code-block:: shell

   $ discos-container build

This creates the ``discos-centos-7.9:latest`` image, unless it already exists.

To remove the provisioned image:

.. code-block:: shell

   $ discos-container remove


Create the container
--------------------

To create the development container:

.. code-block:: shell

   $ discos-container create

The command creates the Docker network if needed, selects an image, creates
the ``manager`` container and waits until it becomes reachable via SSH.

By default, ``create`` uses the ``provisioned`` image if available, otherwise
it falls back to ``latest``.

You can explicitly choose the image:

.. code-block:: shell

   $ discos-container create --image latest
   $ discos-container create --image provisioned

You can also override the inventory and Docker network settings:

.. code-block:: shell

   $ discos-container create --inventory development
   $ discos-container create --network discos_net --subnet 192.168.56.0/24


Start, stop and restart the container
-------------------------------------

Once the container has been created, you can manage its lifecycle with:

.. code-block:: shell

   $ discos-container start
   $ discos-container stop
   $ discos-container restart

The ``start`` and ``restart`` commands wait until the container is reachable
via SSH.


Show container status
---------------------

To inspect the current state of the container and local images:

.. code-block:: shell

   $ discos-container status

This command reports:

- whether the ``manager`` container exists
- whether it is running
- its configured IP address
- whether the ``latest`` and ``provisioned`` images are present


Save and load images
--------------------

To save the current development container to a tar archive:

.. code-block:: shell

   $ discos-container save discos_manager.tar

This command commits the current container to the
``discos-centos-7.9:provisioned`` image and then saves it to the specified
archive.

To load an image archive:

.. code-block:: shell

   $ discos-container load discos_manager.tar


Destroy the container
---------------------

To remove the container:

.. code-block:: shell

   $ discos-container destroy

This command asks for confirmation before deleting the container.


Start and stop DISCOS virtual machines, ``discos-vms``
======================================================

The :file:`discos-vms` script is used to manage DISCOS virtual machines.

To start or stop a virtual machine, specify an action and a machine name.
Supported actions are ``--start``, ``--stop``, ``--status`` and ``--restart``.

For instance, to start the ``manager`` virtual machine:

.. code-block:: shell

   $ discos-vms --start manager
   Starting machine manager..............done.

The ``--start`` command blocks until the machine is booted and reachable.
If the machine is already running, the script prints a message and exits.

The script can also handle multiple machines:

.. code-block:: shell

   $ discos-vms --start manager console

If no machine is specified, the action is applied to all available machines.

To stop a machine:

.. code-block:: shell

   $ discos-vms --stop manager
   Powering off machine manager......done.

The ``--status`` action displays the current machine state.


Login into a deployed machine, ``discos-login``
===============================================

The :file:`discos-login` script acts as a wrapper to ``ssh`` and can be used
to log into a deployed machine.

Example:

.. code-block:: console

   $ discos-login manager
   discos@manager's password:
   (branch?) discos@manager ~ $

You can specify the user with ``-u`` or ``--user``:

.. code-block:: console

   $ discos-login -u observer manager

The script reads host names and IP addresses from the Ansible inventory.


Graphical login into a deployed machine, ``discos-vnc``
=======================================================

The :file:`discos-vnc` script acts as a wrapper to ``vncviewer`` and opens a
graphical session on a deployed machine.

Example:

.. code-block:: console

   $ discos-vnc manager

The command establishes an SSH tunnel and launches the VNC viewer.

To use it, you need a VNC client such as `TigerVNC <https://tigervnc.org/>`_.

On Debian-based systems:

.. code-block:: shell

   $ sudo apt install tigervnc-viewer

On Red Hat-based systems:

.. code-block:: shell

   $ sudo yum install tigervnc

Like :file:`discos-login`, this script relies on the Ansible inventory.
