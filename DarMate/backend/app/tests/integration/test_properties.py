import io

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100


def prop_body(city_id, category_id, **kw):
    return {"city_id": city_id, "category_id": category_id, "title": "Bel appartement S+2", "price": "650.00",
            "rooms": 3, "latitude": "36.8", "longitude": "10.18", **kw}


def make_property(client, h, city_id, category_id, publish=True, **kw):
    r = client.post("/api/v1/properties", json=prop_body(city_id, category_id, publish=publish, **kw), headers=h)
    assert r.status_code == 201, r.text
    return r.json()


def test_owner_can_create_and_public_can_search(api, client, city_id, category_id):
    _, h = api.user("o@test.tn", ["OWNER"])
    make_property(client, h, city_id, category_id)
    make_property(client, h, city_id, category_id, publish=False)  # brouillon : invisible
    r = client.get("/api/v1/properties").json()
    assert r["total"] == 1 and r["items"][0]["title"] == "Bel appartement S+2"


def test_seeker_cannot_publish(api, client, city_id, category_id):
    _, h = api.user("s@test.tn", ["SEEKER"])
    r = client.post("/api/v1/properties", json=prop_body(city_id, category_id), headers=h)
    assert r.status_code == 403


def test_filters_sorting_pagination(api, client, city_id, category_id):
    _, h = api.user("o@test.tn", ["OWNER"])
    for price in ("300", "500", "900"):
        make_property(client, h, city_id, category_id, price=price)
    r = client.get("/api/v1/properties", params={"max_price": 600, "sort": "price_desc"}).json()
    assert [float(i["price"]) for i in r["items"]] == [500.0, 300.0]
    assert client.get("/api/v1/properties", params={"size": 2, "page": 2}).json()["items"].__len__() == 1


def test_idor_other_owner_cannot_edit_or_delete(api, client, city_id, category_id):
    _, owner = api.user("o1@test.tn", ["OWNER"])
    _, attacker = api.user("o2@test.tn", ["OWNER"])
    pid = make_property(client, owner, city_id, category_id)["id"]
    assert client.put(f"/api/v1/properties/{pid}", json={"title": "Piraté"}, headers=attacker).status_code == 404
    assert client.delete(f"/api/v1/properties/{pid}", headers=attacker).status_code == 404
    assert client.patch(f"/api/v1/properties/{pid}/status", json={"status": "SUSPENDED"}, headers=attacker).status_code == 404
    assert client.get(f"/api/v1/properties/{pid}/stats", headers=attacker).status_code == 404
    assert client.get(f"/api/v1/properties/{pid}").json()["title"] == "Bel appartement S+2"


def test_draft_hidden_from_others_but_visible_to_owner(api, client, city_id, category_id):
    _, owner = api.user("o@test.tn", ["OWNER"])
    pid = make_property(client, owner, city_id, category_id, publish=False)["id"]
    assert client.get(f"/api/v1/properties/{pid}").status_code == 404
    assert client.get(f"/api/v1/properties/{pid}", headers=owner).status_code == 200


def test_soft_delete(api, client, city_id, category_id):
    _, owner = api.user("o@test.tn", ["OWNER"])
    pid = make_property(client, owner, city_id, category_id)["id"]
    assert client.delete(f"/api/v1/properties/{pid}", headers=owner).status_code == 204
    assert client.get(f"/api/v1/properties/{pid}").status_code == 404


def test_coliving_rules(api, client, city_id, category_id):
    _, owner = api.user("o@test.tn", ["OWNER"])
    r = client.post("/api/v1/properties", json=prop_body(city_id, category_id, coliving_allowed=True, max_roommates=1), headers=owner)
    assert r.status_code == 422


def test_image_upload_validation(api, client, city_id, category_id):
    _, owner = api.user("o@test.tn", ["OWNER"])
    pid = make_property(client, owner, city_id, category_id)["id"]
    ok = client.post(f"/api/v1/properties/{pid}/images", files={"file": ("a.png", io.BytesIO(PNG), "image/png")}, headers=owner)
    assert ok.status_code == 201
    bad = client.post(f"/api/v1/properties/{pid}/images", files={"file": ("a.php", io.BytesIO(b"<?php"), "application/x-php")}, headers=owner)
    assert bad.status_code == 422
    media = client.get("/media/" + ok.json()["path"])
    assert media.status_code == 200
    assert client.get(f"/api/v1/properties/{pid}").json()["images"][0]["id"] == ok.json()["id"]


def test_private_files_not_publicly_served(client):
    assert client.get("/media/private/identity/1/x.png").status_code == 404


def test_favorites_and_saved_search_alert(api, client, city_id, category_id):
    _, owner = api.user("o@test.tn", ["OWNER"])
    _, seeker = api.user("s@test.tn")
    s = client.post("/api/v1/saved-searches", json={"name": "Tunis pas cher", "filters": {"city_id": city_id, "max_price": 700}, "alert": True}, headers=seeker)
    assert s.status_code == 201
    pid = make_property(client, owner, city_id, category_id)["id"]
    notifs = client.get("/api/v1/notifications", headers=seeker).json()
    assert notifs["unread_count"] == 1 and notifs["items"][0]["type"] == "NEW_PROPERTY"
    assert client.put(f"/api/v1/favorites/{pid}", headers=seeker).status_code == 200
    assert len(client.get("/api/v1/favorites", headers=seeker).json()) == 1
    assert client.get(f"/api/v1/properties/{pid}/stats", headers=owner).json()["favorites"] == 1


def test_map_endpoint(api, client, city_id, category_id):
    _, owner = api.user("o@test.tn", ["OWNER"])
    make_property(client, owner, city_id, category_id)
    assert len(client.get("/api/v1/properties/map").json()) == 1
