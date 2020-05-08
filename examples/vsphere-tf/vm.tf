resource "vsphere_virtual_machine" "vm01" {
  name = "vm01"

  resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id

  num_cpus = 1
  memory   = 1024

  guest_id = "ubuntu64Guest"

  network_interface {
    network_id = data.vsphere_network.network.id
  }

  disk {
    label            = "boot"
    size             = 40
    thin_provisioned = false
  }

  cdrom {
    client_device = true
  }

  clone {
    template_uuid = data.vsphere_virtual_machine.template.id
    customize {
      linux_options {
        host_name = "vm01"
        domain    = "example.org"
      }

      network_interface {
        #
        # Using IP address provided by IPAM
        #
        ipv4_address = restapi_object.ipam_address_vm01.api_data.address
        ipv4_netmask = 24
      }
      ipv4_gateway = "192.168.1.1"
    }
  }
}
