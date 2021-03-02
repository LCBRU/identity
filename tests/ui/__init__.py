def test_missing_route(client):
    resp = client.get("/uihfihihf")
    assert resp.status_code == 404
