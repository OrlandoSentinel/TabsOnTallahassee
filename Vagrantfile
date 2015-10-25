# vi: set ft=ruby

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box = "bento/ubuntu-15.04"

    config.vm.network "private_network", ip: "10.0.0.42"

    config.vm.provider "virtualbox" do |v|
        v.name = "tot"
    end

    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "ansible/tot.yml"
        ansible.inventory_path = "ansible/hosts.vagrant"
        ansible.limit = "all"
        # seems to avoid the delay with private IP not being available
        ansible.raw_arguments = ["-T 30"]
    end
end
