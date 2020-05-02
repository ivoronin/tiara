# https://github.com/Mastercard/terraform-provider-restapi
provider "restapi" {
  uri                   = "http://127.0.0.1:8000"
  username              = "ipam"
  password              = "ipam"
  write_returns_object  = true
  create_returns_object = true
}

resource "restapi_object" "ipam_network" {
  path = "/network"
  data = jsonencode({
    "address" = "10.0.1.0/25"
  })
}

resource "restapi_object" "ipam_range" {
  path = "/network/${restapi_object.ipam_network.id}/range"
  data = jsonencode({
    "start" = "10.0.1.40",
    "stop"  = "10.0.1.50",
  })
}

resource "restapi_object" "ipam_address1" {
  path = "/network/${restapi_object.ipam_network.id}/range/${restapi_object.ipam_range.id}/address"
  data = jsonencode({
    "name" = "example 1"
  })

  provisioner "local-exec" {
    command = "echo IP#1: ${restapi_object.ipam_address1.api_data.address}"
  }
}

resource "restapi_object" "ipam_address2" {
  path = "/network/${restapi_object.ipam_network.id}/range/${restapi_object.ipam_range.id}/address"
  data = jsonencode({
    "name" = "example 2"
  })

  provisioner "local-exec" {
    command = "echo IP#2: ${restapi_object.ipam_address2.api_data.address}"
  }
}

resource "restapi_object" "ipam_address_list" {
  count = 20

  path = "/network/${restapi_object.ipam_network.id}/range/${restapi_object.ipam_range.id}/address"
  data = jsonencode({
    "name" = "example list ${count.index}"
  })
}

