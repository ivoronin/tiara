provider "restapi" {
  uri                   = "http://10.0.1.11:9000"
  username              = "ipam"
  password              = "ipam"
  write_returns_object  = true
  create_returns_object = true
}

provider "vsphere" {
  # Set environment variables
  # VSPHERE_USER
  # VSPHERE_PASSWORD
  # VSPHERE_SERVER
  allow_unverified_ssl = true
}
