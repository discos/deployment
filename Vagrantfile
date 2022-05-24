# -*- mode: ruby -*-
# vi: set ft=ruby :


vagrantfile_api_version = "2"

Vagrant.configure(vagrantfile_api_version) do |config|

    # Common configuration for all virtual machines
    config.vm.synced_folder '.', '/vagrant', disabled: true
    config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--ioapic", "on"]
        vb.memory = 4096
        vb.cpus = 4
        vb.default_nic_type = "virtio"
    end

    # ACS node n.1 (manager)
    config.vm.define "manager" do |node|
        node.vm.hostname = "manager"
        node.vm.box = "bento/centos-6.8"
        node.vm.network :private_network, ip: "192.168.56.200"

        node.vm.provider :virtualbox do |vb|
            vb.name = "discos_manager"
        end
    end
end
