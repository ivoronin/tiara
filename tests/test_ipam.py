
def test_ipam(client):
    # Ensure network list is empty
    response = client.get('/network')
    assert response.status_code == 200
    assert response.json == []

    # Ensure 404 on non-existing entries
    response = client.get('/network/1')
    assert response.status_code == 404

    # Create network #1
    response = client.post('/network', json=dict(address='10.0.0.0/8'))
    assert response.status_code == 200
    network1 = response.json

    # Try to create a network with same address again
    response = client.post('/network', json=dict(address='10.0.0.0/8'))
    assert response.status_code == 400

    # Try to create a network with malformed address
    response = client.post('/network', json=dict(address='10.0.0.0+8'))
    assert response.status_code == 400

    # Try to create a network overlapping with network #1
    response = client.post('/network', json=dict(address='10.0.0.0/16'))
    assert response.status_code == 400

    # Create network #2
    response = client.post('/network', json=dict(address='192.168.0.0/24'))
    assert response.status_code == 200
    network2 = response.json

    # Ensure both networks are present in the network list
    response = client.get('/network')
    assert response.status_code == 200
    assert response.json == [network1, network2]

    # Delete network #1
    response = client.delete(f'/network/{network1["id"]}')
    assert response.status_code == 200

    # Ensure only second network is present in the network list
    response = client.get('/network')
    assert response.status_code == 200
    assert response.json == [network2]

    # Create network #3
    response = client.post('/network', json=dict(address='100.0.0.0/16'))
    assert response.status_code == 200
    network3 = response.json

    # Ensure that ranges list is empty
    response = client.get(f'/network/{network2["id"]}/range')
    assert response.status_code == 200
    assert response.json == []

    # Try to create range with a network address
    response = client.post(f'/network/{network2["id"]}/range', json=dict(
        start='192.168.0.0',
        stop='192.168.0.110',
    ))
    assert response.status_code == 400

    # Try to create range with a boadcast address
    response = client.post(f'/network/{network2["id"]}/range', json=dict(
        start='192.168.0.1',
        stop='192.168.0.255',
    ))
    assert response.status_code == 400

    # Try to create range with malformed IPs
    response = client.post(f'/network/{network2["id"]}/range', json=dict(
        start='999.168.0.10',
        stop='192.168.0.100',
    ))
    assert response.status_code == 400

    # Create range #1
    response = client.post(f'/network/{network2["id"]}/range', json=dict(
        start='192.168.0.10',
        stop='192.168.0.100',
    ))
    assert response.status_code == 200
    range1 = response.json

    # Ensure range #1 is now in the list
    response = client.get(f'/network/{network2["id"]}/range')
    assert response.status_code == 200
    assert response.json == [range1]

    # Try to create overlapping range
    response = client.post(f'/network/{network2["id"]}/range', json=dict(
        start='192.168.0.50',
        stop='192.168.0.110',
    ))
    assert response.status_code == 400

    # Try to create out-of-network range
    response = client.post(f'/network/{network2["id"]}/range', json=dict(
        start='192.168.1.50',
        stop='192.168.1.110',
    ))
    assert response.status_code == 400

    # Create range #2
    response = client.post(f'/network/{network2["id"]}/range', json=dict(
        start='192.168.0.200',
        stop='192.168.0.202',
    ))
    assert response.status_code == 200
    range2 = response.json

    # Ensure both ranges are present
    response = client.get(f'/network/{network2["id"]}/range')
    assert response.status_code == 200
    assert response.json == [range1, range2]

    # Create range #3
    response = client.post(f'/network/{network3["id"]}/range', json=dict(
        start='100.0.10.0',
        stop='100.0.11.1',
    ))
    assert response.status_code == 200
    range3 = response.json

    # Ensure that only range3 is present for network3
    response = client.get(f'/network/{network3["id"]}/range')
    assert response.status_code == 200
    assert response.json == [range3]

    # Delete range #1
    response = client.delete(f'/network/{network2["id"]}/range/{range1["id"]}')
    assert response.status_code == 200

    # Request address using wrong range
    response = client.post(f'/network/{network2["id"]}/range/{range3["id"]}/address', json=dict(name="test1"))
    assert response.status_code == 404

    # Request address #1
    response = client.post(f'/network/{network2["id"]}/range/{range2["id"]}/address', json=dict(name="test1"))
    assert response.status_code == 200
    address1 = response.json
    assert address1['address'] == '192.168.0.200'

    # Request address #2
    response = client.post(f'/network/{network2["id"]}/range/{range2["id"]}/address', json=dict(name="test2"))
    assert response.status_code == 200
    address2 = response.json
    assert address2['address'] == '192.168.0.201'

    # Request address #3
    response = client.post(f'/network/{network2["id"]}/range/{range2["id"]}/address', json=dict(name="test3"))
    assert response.status_code == 200
    address3 = response.json
    assert address3['address'] == '192.168.0.202'

    # Request address #4 (Too much)
    response = client.post(f'/network/{network2["id"]}/range/{range2["id"]}/address', json=dict(name="test4"))
    assert response.status_code == 404

    # Get address #3
    response = client.get(f'/network/{network2["id"]}/range/{range2["id"]}/address/{address3["id"]}')
    assert response.status_code == 200
    assert response.json == address3

    # Delete address #2
    response = client.delete(f'/network/{network2["id"]}/range/{range2["id"]}/address/{address2["id"]}')
    assert response.status_code == 200

    # Request address #5
    response = client.post(f'/network/{network2["id"]}/range/{range2["id"]}/address', json=dict(name="test5"))
    assert response.status_code == 200
    address5 = response.json
    assert address5['address'] == '192.168.0.201'

    # Delete network
    response = client.delete(f'/network/{network2["id"]}')
    assert response.status_code == 200

    # Request address #6
    response = client.post(f'/network/{network3["id"]}/range/{range3["id"]}/address', json=dict(name="test6"))
    assert response.status_code == 200
    address6 = response.json
    assert address6['address'] == '100.0.10.0'

    # Try to break stuff by updating ranges and networks
    response = client.put(f'/network/{network3["id"]}/range/{range3["id"]}',
                          json=dict(start='100.0.10.1', stop='100.0.11.1'))
    assert response.status_code == 400

    response = client.put(f'/network/{network3["id"]}', json=dict(address='100.0.0.0/24', ))
    assert response.status_code == 400

    # Valid PUTS
    response = client.put(f'/network/{network3["id"]}/range/{range3["id"]}',
                          json=dict(start='100.0.10.0', stop='100.0.12.1'))
    assert response.status_code == 200

    response = client.put(f'/network/{network3["id"]}', json=dict(address='100.0.0.0/8', ))
    assert response.status_code == 200

    # Get all addresses
    response = client.get(f'/network/{network3["id"]}/range/{range3["id"]}/address')
    assert response.status_code == 200


def test_auth(client):  # pylint: disable=C0116
    response = client.get('/network')
    assert response.status_code != 401

    response = client.get('/network', credentials='wrong-data')
    assert response.status_code == 401

    response = client.get('/network', disable_auth=True)
    assert response.status_code == 401


def test_health(client):  # pylint: disable=C0116
    response = client.get('/healthz')
    assert response.status_code == 200
