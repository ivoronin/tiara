# Create network resource
resource "restapi_object" "ipam_network_lan" {
  path = "/network"
  data = jsonencode({
    "address" = "192.168.1.0/24"
  })
}

# Create address range resource
resource "restapi_object" "ipam_range_lan_vms" {
  path = "/network/${restapi_object.ipam_network_lan.id}/range"
  data = jsonencode({
    "start" = "192.168.1.10",
    "stop"  = "192.168.1.100",
  })
}

# Request next available IP address
resource "restapi_object" "ipam_address_vm01" {
  path = "/network/${restapi_object.ipam_network_lan.id}/range/${restapi_object.ipam_range_lan_vms.id}/address"
  data = jsonencode({
    "name" = "vm01"
  })
}
