.. _dependencies:

************
Dependencies
************

To automatically deploy DISCOS, you need to install four dependencies:
`Git <https://git-scm.com/>`_, `Ansible <https://www.ansible.com/>`_,
`Vagrant <https://www.vagrantup.com/>`_ and `VirtualBox
<https://www.virtualbox.org/>`_.  It usually takes about 15 minutes.


Install Git
===========
Before installing Git, verify if it is already installed:

.. code-block:: shell

   $ git --version
   git version 1.9.1

You do not need a particular version of Git, but if the command ``git --version``
fails, than you have to install Git by following the instructions at the `official Git
website <https://git-scm.com/book/en/v1/Getting-Started-Installing-Git>`_.

Install Ansible
===============
Verify if Alsible is already installed:

.. code-block:: shell

   ansible --version
   ansible 2.3.2.0

If the command ``ansible --version`` fails, than install Ansible by
executing the following command:

.. code-block:: shell

    $ pip install "ansible==2.3.2"

In case the ``pip install`` command fails, try to install Ansible
(greater than 2.0, lesser than 2.4, otherwise the provisioning procedure could fail)
as explained in the `official ansible website
<http://docs.ansible.com/ansible/intro_installation.html#installation>`_.


Install VirtualBox and Vagrant
==============================
You need to install VirtualBox and Vagrant only if you want to
deploy DISCOS on VMs, as in the case of a development environment.
As a first step, check if VirtualBox is already installed:

.. code-block:: shell

   $ which virtualbox 
   /usr/bin/virtualbox

In case it is not, download the binary file from the
`official website <https://www.virtualbox.org/wiki/Downloads>`_
and install it.
Now verify if Vagrant is already installed:

.. code-block:: shell

   $ vagrant --version
   Vagrant 1.8.6

If it is not, download the binary file from
the `vagrant official website <https://www.vagrantup.com/downloads.html>`_
and install it.
At this point you are ready to deploy DISCOS.  The :ref:`deploy_quickstart`
section is a good starting point, because it covers a typical scenario.
