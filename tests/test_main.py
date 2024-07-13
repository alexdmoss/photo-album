
def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "<li>site_name: Photo Slideshow</li>" in response.text
    assert "<li>page_title: Home</li>" in response.text
    assert "<li>page_description: Photo Slideshow</li>" in response.text
