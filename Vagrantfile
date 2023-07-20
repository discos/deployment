# -*- mode: ruby -*-
# vi: set ft=ruby :


vagrantfile_api_version = "2"

Vagrant.configure(vagrantfile_api_version) do |config|

    # Common configuration for all virtual machines
    config.vm.synced_folder '.', '/vagrant', disabled: true
    config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--ioapic", "on"]
        vb.memory = 8192
        vb.cpus = 4
        vb.default_nic_type = "virtio"
    end

    config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "/tmp/id_rsa.pub"
    config.vm.provision "shell", "inline" => "mkdir '/root/.ssh' && touch '/root/.ssh/authorized_keys'"
    config.vm.provision "shell", "inline" => "cat '/tmp/id_rsa.pub' >> '/root/.ssh/authorized_keys'"
    config.vm.provision "shell", "inline" => "rm '/tmp/id_rsa.pub'"

    # ACS node n.1 (manager)
    config.vm.define "manager" do |node|
        node.vm.hostname = "manager"
        node.vm.box = "bento/centos-7"
        node.vm.network :private_network, ip: "192.168.56.200"

        node.vm.provider :virtualbox do |vb|
            vb.name = "discos_manager"
        end
    end
end
