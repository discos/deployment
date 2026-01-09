.. _deploy_production:

**********
Production
**********

Unlike the development environment, that uses Vagrant pre-configured virtual
machines, when dealing with production machines, you have to perform some
preliminary tasks in order for the provisioning procedure to be completed
successfully. It is required that you configure the to-be-provisioned
machines' network interfaces, as well as their disk partitions. You also have
to install on them the desired Operating System (Centos 6.8 for ACS running
machines, Centos 7.2 for storage). Without these preliminary tasks, the
provisioning procedure will most likely fail.

Machines deployment
===================
To deploy the system in production, you have to specify a *cluster* of machines,
followed by the name of the station, you can choose among ``Medicina``,
``Noto`` or ``SRT``:

.. code-block:: shell

  $ discos-deploy discos:SRT

As mentioned in the :ref:`deploy_development` section, the ``discos`` *cluster*
makes the automatic procedure provision the whole DISCOS system, composed by
all the required station machines. If you only want to deploy a single machine,
change the cluster from ``discos`` to the related machine name. For instance,
in the following case we are deploying only the ``console`` machine for the
``SRT`` station:

.. code-block:: shell

  $ discos-deploy console:SRT


DISCOS setup
============

Manual setup
------------
To install the DISCOS control software, you can use the ``discos-get`` command
and then build and install the system by yourself, as we already saw in the
:ref:`get_a_discos_branch` paragraph. Since this time we are deploying in a
production environment, you may want to deploy a DISCOS tag. The ``discos-get``
script can handle this case just like it does for normal branches. All you have
to do is pass to the scripts command line the ``--tag`` argument instead of the
``--branch`` one. Of course, you also have to specify the desired DISCOS tag
afterwards:

.. figure:: images/discos1rc2.png
   :figwidth: 100%
   :align: center

The downloaded tag will be handled by ``discos-get`` and ``discos-set`` just
like a normal branch.

.. note:: As you may have noticed from the last image, the downloaded
   repository will be left in a ``detached HEAD' state``. This means that any
   modification you make to the repository will not be tracked by any remote
   branch. If you want to edit some files in order to push a hotfix you should
   download and work on the ``stable`` branch.

You can now build and install the DISCOS control system as we already saw in
the :ref:`install_discos` paragraph.

Automatic setup
---------------
The ``discos-deploy`` script can automatically handle the DISCOS setup
procedure even for tags. In order for it to do this, you have to pass the
``--tag`` argument to the ``discos-deploy`` command, followed by the DISCOS
tag you want to install on the machines:

.. code-block:: shell

   $ discos-deploy discos:SRT --tag discos1.0-rc02


.. note:: Since you are performing the deployment procedure on station
   machines, the station name is already specified inside the machines
   themselves as an environment variable, so you can omit the ``--station``
   argument from both the ``discos-deploy`` and ``discos-get`` scripts. If you
   pass the ``--station`` argument anyway, if the given argument does not match
   the correct station you will receive an error and the procedure will stop.

Replace the Manager in case of failure
--------------------------------------
In case the Manager machine suffers a failure of some sort, it has to be
replaced. In order to do this, the first thing to do is, perform the
provisioning procedure on a newly installed machine (after putting the new
Manager's IP address in the Ansible inventory's hosts file). In order
for the whole system to behave correctly it is also necessary to perform
some manual tweaking on the other DISCOS machines as well (in case the
DISCOS control system is running on a distributed environment. This is the
case for the SRT and Medicina stations).

The tweaks to be performed in order for the DISCOS control system to work as
expected are the following:

- Replace the old ACS Manager IP address reference with the new one in
  ``/discos-sw/config/misc/bash_profile`` file in the ``discos-console``
  machine. It is stored as an environment variable called ``MNG_IP``.
- Replace the old Manager IP address with the new one in some fiels in the
  DISCOS CDB. More specifically, one file has to be corrected in order for the
  control system to be able to properly communicate with the ``TotalPower``
  backend, you can find this file in the repository of the currently deployed
  released of DISCOS, under the directory
  ``SRT/Configuration/CDB/alma/BACKENDS/TotalPower/TotalPower.xml``.
  The variable to be corrected is called ``DataIPAddress``. This has to be
  performed on the new Manager machine itself before launching the control
  system.
- Make sure that all the station systems and machines accept incoming
  connections from the newly allocated Manager's IP address. Specifically, the
  ``TotalPower`` backend and the ``CalMux`` machines have to be tweaked in
  order to allow them to be controlled by the new manager.

In order for the whole environment to work properly is also necessary to
perform some other tweaks on the other DISCOS machines, but not related to
the control system itself:

- Replace the old Manager IP address with the new one in ``/etc/hosts`` file in
  ``discos-console`` and ``discos-storage`` machines (in case the DISCOS
  control software is running on a distributed environment). This will allow
  other services such as the Lustre service on the ``discos-storage`` machine
  to point again to the correct IP address.
- Perform the ssh key exchange procedure between the ``discos`` user of the
  newly installed Manager with the ones present on the ``discos-console`` and
  ``discos-storage`` machines. The same procedure has to be performed between
  the ``root`` users as well. This will allow some scripts such as the Lustre
  service on the ``discos-storage`` machine and the ``discos-addProject`` and
  ``discos-removeProject`` on the ``discos-console`` machine to perform some
  remote tasks that would be impossible to be performed otherwise.
