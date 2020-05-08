# Tiara - Tiny IP Address Registry API Server
Simple and lightweight IPAM server with a clean REST API.
Intended to be used with [Terraform](https://www.terraform.io/) and other infrastructure automation tools.

## Deployment
A Docker container for Tiara is available from Docker Hub
```shell
docker run -d --name tiara \
  -e IPAM_USERNAME=ipam \
  -e IPAM_PASSWORD=ipam \
  -e IPAM_DATABASE_URI=sqlite:////data/ipam.db \
  -p 8000:8000 -v /data:/data \
  ivoronin/tiara:latest
```
PostgreSQL and MySQL are supported too. Check SQLAlchemy docs for the connection URI format.

## Terraform example
This example uses [REST API provider](https://github.com/Mastercard/terraform-provider-restapi/).
Please also see `examples/vsphere-tf` for complete example of using Tiara together with Terraform in vSphere environment.

```terraform
provider "restapi" {
  uri                   = "http://127.0.0.1:8000"
  username              = "ipam"
  password              = "ipam"
  write_returns_object  = true
  create_returns_object = true
}

# Create network resource
resource "restapi_object" "ipam_network" {
  path = "/network"
  data = jsonencode({
    "address" = "10.0.1.0/25"
  })
}

# Create range resource
resource "restapi_object" "ipam_range" {
  path = "/network/${restapi_object.ipam_network.id}/range"
  data = jsonencode({
    "start" = "10.0.1.40",
    "stop"  = "10.0.1.50",
  })
}

# Obtain next available IP address
resource "restapi_object" "ipam_address" {
  path = "/network/${restapi_object.ipam_network.id}/range/${restapi_object.ipam_range.id}/address"
  data = jsonencode({
    "name" = "example"
  })
}

# Obtained value is accessible as ${restapi_object.ipam_address.api_data.address}
```

# REST API Reference
- When sending a POST or PUT request, all parameters should be passed in the request body as JSON
- Server returns the object created on all write operations (POST, PUT)
- Basic HTTP authentication is being used
- Server prohibits creation of overlapping networks and ranges
- Various other integrity checks are implemented

## Network
### Schema
```json
{
  "id": "integer",
  "address": "string"
}
```
### Methods
- List all networks: `GET /network`
- Create network: `POST /network`, required parameters: `address` ('10.0.0.0/8')
- Read network: `GET /network/<network_id>`
- Update network: `PUT /network/<network_id>`, required parameters: `address` ('10.0.0.0/8')
- Delete network: `DELETE /network/<network_id>`

## Range
### Schema
```json
{
  "id": "integer",
  "start": "string",
  "stop": "string",
  "network_id": "integer"
}
```
### Methods
- List all ranges: `GET /network/<network_id>/range`
- Create range: `POST /network/<network_id>/range`, required parameters: `start` ('10.0.0.10'), `stop` ('10.0.0.99')
- Read range: `GET /network/<network_id>/range`
- Update network: `PUT /network/<network_id>/range/<range_id>`, required parameters: `start` ('10.0.0.10'), `stop` ('10.0.0.99')
- Delete network: `DELETE /network/<network_id>/range`

## Address
### Schema
```json
{
  "id": "integer",
  "address": "string",
  "name": "string",
  "range_id": "integer"
}
```
### Methods
- List all addresses: `GET /network/<network_id>/range/<range_id>/address`
- Create (request next available) address: `POST /network/<network_id>/range/<range_id>/address`, required parameters: `name` (string)
- Read address: `GET /network/<network_id>/range/<range_id>/address/<address_id>`
- Update address: `PUT /network/<network_id>/range/<range_id>/address/<address_id>`, required parameters: `name` (string)
- Delete address: `DELETE /network/<network_id>/range/<range_id>/address/<address_id>`
