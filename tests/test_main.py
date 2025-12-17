
def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Photo Albums" in response.text
    assert "Please log in to view photos" in response.text
