def test_flash_after_create_habit(auth_client):
    auth_client.post(
        "/habits/new",
        data={"name": "FlashTest", "color": "#000000"},
        follow_redirects=False,
    )
    r = auth_client.get("/")
    assert "flash--success" in r.text
    assert "FlashTest" in r.text


def test_flash_disappears_on_next_page(auth_client):
    auth_client.post("/habits/new", data={"name": "X"}, follow_redirects=False)
    first = auth_client.get("/")
    assert "flash--success" in first.text
    second = auth_client.get("/")
    assert "flash--success" not in second.text


def test_flash_after_delete(auth_client):
    auth_client.post("/habits/new", data={"name": "ToDel"}, follow_redirects=False)
    auth_client.get("/")  
    auth_client.post("/habits/1/delete", follow_redirects=False)
    r = auth_client.get("/")
    assert "flash--info" in r.text or "flash--success" in r.text
    assert "удалена" in r.text


def test_flash_after_edit(auth_client):
    auth_client.post("/habits/new", data={"name": "X"}, follow_redirects=False)
    auth_client.get("/")  
    auth_client.post(
        "/habits/1/edit",
        data={"name": "Y", "description": "", "color": "#000000"},
        follow_redirects=False,
    )
    r = auth_client.get("/habits/1")
    assert "flash--success" in r.text
    assert "обновлена" in r.text
