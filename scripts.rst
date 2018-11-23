.. _deploy_scripts:

**************
Useful scripts
**************

If you executed the ``setup.py`` script as mentioned in the
:ref:`deploy_quickstart` section, you will have access via terminal to the
following useful scripts, along with the :file:`discos_deploy` one (described
in the :ref:`deploy_quickstart` section):

- :file:`discos-vms`: a script used to manage DISCOS virtual machines
- :file:`discos-login`: a script that performs SSH login to the specified virtual machine
- :file:`discos-vnc`: a script that opens a VNC viewer to the specified virtual machine


Start and stop DISCOS virtual machines, `discos-vms`
====================================================
To start or stop a DISCOS virtual machine, you can run the :file:`discos-vms`
script specifying an action and a machine. The action is one among `--start`,
`--stop`, `--status` and `--restart`, the machine argument is the name of an
already deployed virtual machine. For instance, if you want to start the
``manager`` virtual machine, all you have to do is execute the following command:

.. code-block:: shell

   $ discos-vms --start manager
   Starting machine manager..............done.

As you may have noticed from the previous examples, the ``discos-vms --start <machine>``
command will block and wait until the machine is booted up and ready.
Executing this command when the selected machine is already powered on will just
print on screen:

.. code-block:: shell

   $ discos-vms --start manager
   Machine manager is already running.

The script can also handle multiple machines:

.. code-block:: shell

   $ discos-vms --start manager console
   Starting machine manager..............done.
   Starting machine console..............done.

If you omit the machine, the script will try to execute the same action on all
available machines:

.. code-block:: shell

   $ discos-vms --start
   Starting machine storage..............done.
   Starting machine manager..............done.
   Starting machine console..............done.


.. note:: Right after the deployment procedure is completed, the deployed
   virtual machines will be running already, so starting them with the above
   command will just output ``Machine <machine> is already running``.


If you want to stop a running machine you just need to specify the ``--stop``
action:

.. code-block:: shell

   $ discos-vms --stop manager
   Powering off machine manager......done.

Just like the ``--start`` command, the ``--stop`` command will block and wait
until the selected machine has been completely powered off. Trying to stop
a powered off machine will print a message just like the ``--start`` command:

.. code-block:: shell

   $ discos-vms --stop manager
   Machine manager is not running.

If you use the ``--restart`` action, machines will of course be restarted.

In case you specify the ``--status`` action, the script will display the
virtual machine status:

.. code-block:: shell

   $ discos-vms --status manager console
   Machine manager status: running.
   Machine console status: powered off.


Login into a DISCOS virtual machine, `discos-login`
===================================================
The script :file:`discos-login` acts as a wrapper to `ssh`, and is useful to
easily perform login on a deployed virtual machine. To login into a DISCOS
virtual machine with this script, you can simply execute the following code:

.. code-block:: shell

   $ discos-login manager
   discos@manager's password:
   (branch?) discos@manager ~ $

The `discos-login` command handles the login procedure by internally executing
the following command:

.. code-block:: shell

   $ ssh -CX discos@manager

You can specify the user with which you want to login to the virtual machine,
by appending the ``-u``, or ``--user``, argument, followed by the desired user
name, to the `discos-login` script, just as follows:

.. code-block:: shell

   $ discos-login -u observer console
   observer@console's password:
   (branch?) observer@console ~ $


.. note:: Currently the ``discos-login`` command only handles logins to virtual
   machines. It does not rely on host names present in the ``/etc/hosts`` file,
   it reads host names and their IP addresses from the Ansible inventory
   directory. Changing any development machine's IP address in the Ansible
   inventory after the deployment procedure is completed could result in a
   login failure using this script. This behavior could change in the future
   in order to enable the login to any machine (even actual ones).


Graphical login into a DISCOS virtual machine (using VNC), `discos-vnc`
=======================================================================
The script :file:`discos-vnc` acts as a wrapper to ``vncviewer``, and is useful
to perform a graphical login on a deployed virtual machine.

In order to be able to use it you should install ``vncviewer``, we suggest the
``tigervnc`` one, that can be installed via ``yum`` or ``apt``. On red-hat
based linux distributions you can install it by typing:

.. code-block:: shell

   $ sudo yum install tigervnc

Whether on debian-based linux distributions you can install it by typing:

.. code-block:: shell

   $ sudo apt install tigervnc-viewer

If you fail to install the ``vncviewer`` using the previous commands, or if you
are running a different operating system than the previously mentioned ones,
check out the `official tigervnc website <https://tigervnc.org/>`_.


Once you installed the ``vncviewer``, you can correctly execute the
``discos-vnc`` command. In order to login into a DISCOS virtual machine by the
means of it, you can simply execute the following code and insert type desired
user's login password:

.. code-block:: shell

   $ discos-vnc manager
   discos@manager's password:

At this point the VNC session will be opened on your display.
The :file:`discos-vnc` command handles the graphical login procedure by
establishing a ssh tunnel to the desired machine and launching the
``vncviewer`` in order to display the specified user's desktop. Only the
``manager`` and ``console`` machines hosts some VNC servers. The ``manager``
machine hosts the VNC server for the ``discos`` user, the ``console`` machine
hosts both the VNC servers for the ``discos`` user and the ``observer`` user.


.. note:: Like the `discos-login` script, even `discos-vnc` relies on IP
   addresses read from the Ansible inventory directory. This behavior could
   change in the future in order to enable the graphical login to any machine
   (even actual ones).
