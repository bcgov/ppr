

def test_det_message(client):

    queue_ce_message = b'{"datacontenttype": "application/json", "id": "3f25e888-0166-45aa-ae5d-eb2c695e635f", "source": null, "specversion": "1.0", "subject": null, "time": "2021-12-19T23:49:06.082250+00:00", "type": null}'

    rc = client.post('/', data=queue_ce_message)

    print(rc)

    assert rc.status_code == 200
