# -*- mode: ruby -*-
# vi: set ft=ruby :
require 'etc'

vagrantfile_api_version = "2"

Vagrant.configure(vagrantfile_api_version) do |config|
    config.ssh.username = 'root'
    config.ssh.password = 'vagrant'
    config.ssh.insert_key = false

    # Common configuration for all virtual machines
    config.vm.synced_folder '.', '/vagrant', disabled: true
    config.vm.provider :virtualbox do |vb|
        vb.customize ["modifyvm", :id, "--ioapic", "on"]
        vb.memory = [8192, `free -m | awk '/^Mem:/ {print $2/2}'`.to_i].min
        vb.cpus = [4, (Etc.nprocessors / 2.0).ceil].min
        vb.default_nic_type = "virtio"
    end

    config.vm.provision "file", run: "always", source: "#{ENV['HOME']}/.ssh/id_rsa.pub", destination: "/tmp/id_rsa.pub"
    config.vm.provision "shell", run: "always", "inline": <<-SCRIPT
        mkdir -p '/root/.ssh' && touch '/root/.ssh/authorized_keys'
        if [ $(grep "$(cat /tmp/id_rsa.pub)" /root/.ssh/authorized_keys | wc -l) == 0 ]; then
            cat '/tmp/id_rsa.pub' >> '/root/.ssh/authorized_keys'
        fi
        rm '/tmp/id_rsa.pub'
    SCRIPT
    config.vm.provision "shell", "inline" => "sed -i -e 's/NM_CONTROLLED=yes/NM_CONTROLLED=no/g' /etc/sysconfig/network-scripts/ifcfg-eth1"
    config.vm.provision "shell", "inline" => "usermod -m -d /vagrant vagrant"

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
