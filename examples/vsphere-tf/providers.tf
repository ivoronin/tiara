provider "restapi" {
  uri                   = "http://127.0.0.1:8000"
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
