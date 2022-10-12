from main import app
import pytest


@pytest.fixture
def client():
    return app.test_client()


def test_service(client):
    resp = client.post('/readings', json={
        "time": "2022-09-12T17:47:03Z",
        "label": "garage,window",
        "reading": 69})
    assert resp.status_code == 200
    assert resp.json.get('Success')


def test_service_no_json_body(client):
    resp = client.post('/readings', data='something')
    assert resp.status_code == 415
    assert resp.json.get('error')


def test_service_wrong_type(client):
    resp = client.post('/readings', json={
        "time": "2022-09-12T17:47:03Z",
        "label": "garage,window",
        "reading": "69"})
    assert resp.status_code == 400
    assert resp.json.get('error')


def test_service_not_iso(client):
    resp = client.post('/readings', json={
        "time": "12092022",
        "label": "garage,window",
        "reading": 69})
    assert resp.status_code == 400
    assert resp.json.get('error')


def test_service_http_method(client):
    resp = client.get('/readings?room=bedroom'
                      '&since=2022-08-20T20:00:00'
                      '&until=2022-10-13T20:00:00')
    assert resp.status_code == 200


def test_service_http_no_data(client):
    resp = client.get('/readings?room=bedroom'
                      '&since=2022-08-20T20:00:00'
                      '&until=2022-10-13T20:00:00')
    assert resp.status_code == 200


def test_service_bad_http_method(client):
    resp = client.get('/readings')
    assert resp.status_code == 404
