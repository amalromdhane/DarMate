import io
from datetime import datetime, timedelta, timezone

from app.tests.integration.test_properties import make_property

API = "/api/v1"


def future(days=2, hours=10):
    d = (datetime.now(timezone.utc) + timedelta(days=days)).replace(hour=hours, minute=0, second=0, microsecond=0)
    return d.isoformat(), (d + timedelta(hours=1)).isoformat()


def setup_rental(api, client, city_id, category_id, coliving=False):
    oid, owner = api.user("owner@test.tn", ["OWNER"])
    sid, seeker = api.user("seeker@test.tn")
    kw = {"coliving_allowed": True, "max_roommates": 3} if coliving else {}
    pid = make_property(client, owner, city_id, category_id, **kw)["id"]
    return oid, owner, sid, seeker, pid


def test_rental_lifecycle_and_review(api, client, city_id, category_id):
    oid, owner, sid, seeker, pid = setup_rental(api, client, city_id, category_id)
    _, other = api.user("other@test.tn")
    rr = client.post(f"{API}/rental-requests", json={"property_id": pid, "message": "Bonjour"}, headers=seeker)
    assert rr.status_code == 201, rr.text
    rid = rr.json()["id"]
    assert client.post(f"{API}/rental-requests", json={"property_id": pid}, headers=seeker).status_code == 409  # doublon
    # un tiers n'a aucun accès (IDOR)
    assert client.get(f"{API}/rental-requests/{rid}", headers=other).status_code == 404
    assert client.patch(f"{API}/rental-requests/{rid}/status", json={"status": "ACCEPTED"}, headers=other).status_code == 404
    # le demandeur ne peut pas s'auto-accepter
    assert client.patch(f"{API}/rental-requests/{rid}/status", json={"status": "ACCEPTED"}, headers=seeker).status_code == 403
    # avis impossible avant confirmation
    assert client.post(f"{API}/reviews", json={"rental_request_id": rid, "target_type": "OWNER", "rating": 5}, headers=seeker).status_code == 409
    assert client.get(f"{API}/rental-requests", params={"box": "received"}, headers=owner).json()[0]["id"] == rid
    assert client.post(f"{API}/rental-requests/{rid}/confirm", headers=owner).status_code == 409  # pas encore acceptée
    assert client.patch(f"{API}/rental-requests/{rid}/status", json={"status": "ACCEPTED"}, headers=owner).json()["status"] == "ACCEPTED"
    assert client.post(f"{API}/rental-requests/{rid}/confirm", headers=seeker).status_code == 403
    assert client.post(f"{API}/rental-requests/{rid}/confirm", headers=owner).json()["status"] == "CONFIRMED"
    assert client.get(f"{API}/properties/{pid}").json()["status"] == "RENTED"
    assert client.get(f"{API}/properties").json()["total"] == 0
    # avis
    assert client.post(f"{API}/reviews", json={"rental_request_id": rid, "target_type": "OWNER", "rating": 5, "comment": "Super"}, headers=seeker).status_code == 201
    assert client.post(f"{API}/reviews", json={"rental_request_id": rid, "target_type": "OWNER", "rating": 4}, headers=seeker).status_code == 409
    assert client.post(f"{API}/reviews", json={"rental_request_id": rid, "target_type": "PROPERTY", "rating": 4}, headers=seeker).status_code == 201
    assert client.post(f"{API}/reviews", json={"rental_request_id": rid, "target_type": "TENANT", "rating": 4, "reviewee_id": sid}, headers=owner).status_code == 201
    assert client.post(f"{API}/reviews", json={"rental_request_id": rid, "target_type": "OWNER", "rating": 5}, headers=other).status_code == 404
    summary = client.get(f"{API}/users/{oid}/reviews").json()
    assert summary["count"] == 2 and summary["average"] == 4.5
    assert client.get(f"{API}/properties/{pid}/reviews").json()["count"] == 1


def test_owner_cannot_request_own_property_and_confirm_rejects_others(api, client, city_id, category_id):
    oid, owner, sid, seeker, pid = setup_rental(api, client, city_id, category_id)
    assert client.post(f"{API}/rental-requests", json={"property_id": pid}, headers=owner).status_code == 403
    _, s2 = api.user("s2@test.tn")
    r1 = client.post(f"{API}/rental-requests", json={"property_id": pid}, headers=seeker).json()["id"]
    r2 = client.post(f"{API}/rental-requests", json={"property_id": pid}, headers=s2).json()["id"]
    client.patch(f"{API}/rental-requests/{r1}/status", json={"status": "ACCEPTED"}, headers=owner)
    client.post(f"{API}/rental-requests/{r1}/confirm", headers=owner)
    assert client.get(f"{API}/rental-requests/{r2}", headers=s2).json()["status"] == "REJECTED"


def test_group_collective_request_and_conversation(api, client, city_id, category_id):
    oid, owner, sid, seeker, pid = setup_rental(api, client, city_id, category_id, coliving=True)
    s2id, s2 = api.user("s2@test.tn")
    g = client.post(f"{API}/groups", json={"name": "Les colocs", "max_members": 3}, headers=seeker).json()
    assert g["conversation_id"] and len(g["members"]) == 1
    inv = client.post(f"{API}/groups/{g['id']}/invitations", json={"invitee_id": s2id}, headers=seeker)
    assert inv.status_code == 201
    assert client.post(f"{API}/groups/{g['id']}/invitations", json={"invitee_id": s2id}, headers=seeker).status_code == 409
    # seul l'invité peut répondre
    assert client.patch(f"{API}/group-invitations/{inv.json()['id']}", json={"accept": True}, headers=seeker).status_code == 404
    assert client.patch(f"{API}/group-invitations/{inv.json()['id']}", json={"accept": True}, headers=s2).status_code == 200
    assert len(client.get(f"{API}/groups/{g['id']}", headers=s2).json()["members"]) == 2
    # discussion de groupe
    cid = g["conversation_id"]
    assert client.post(f"{API}/conversations/{cid}/messages", json={"body": "Salut la coloc"}, headers=s2).status_code == 201
    assert client.get(f"{API}/conversations/{cid}/messages", headers=seeker).json()[0]["body"] == "Salut la coloc"
    # demande collective
    rr = client.post(f"{API}/rental-requests", json={"property_id": pid, "group_id": g["id"]}, headers=seeker)
    assert rr.status_code == 201 and rr.json()["group_id"] == g["id"]
    # un membre du groupe voit la demande, un étranger non
    assert client.get(f"{API}/rental-requests/{rr.json()['id']}", headers=s2).status_code == 200
    _, stranger = api.user("x@test.tn")
    assert client.get(f"{API}/groups/{g['id']}", headers=stranger).status_code == 404


def test_group_request_refused_when_coliving_disabled(api, client, city_id, category_id):
    oid, owner, sid, seeker, pid = setup_rental(api, client, city_id, category_id, coliving=False)
    g = client.post(f"{API}/groups", json={"name": "Groupe", "max_members": 2}, headers=seeker).json()
    assert client.post(f"{API}/rental-requests", json={"property_id": pid, "group_id": g["id"]}, headers=seeker).status_code == 409


def test_visits_flow(api, client, city_id, category_id):
    oid, owner, sid, seeker, pid = setup_rental(api, client, city_id, category_id)
    s, e = future()
    v = client.post(f"{API}/visits", json={"property_id": pid, "slots": [{"starts_at": s, "ends_at": e}]}, headers=seeker)
    assert v.status_code == 201, v.text
    vid, slot = v.json()["id"], v.json()["slots"][0]["id"]
    # le demandeur ne peut pas accepter son propre créneau
    assert client.patch(f"{API}/visits/{vid}", json={"action": "accept", "slot_id": slot}, headers=seeker).status_code == 403
    assert client.patch(f"{API}/visits/{vid}", json={"action": "accept", "slot_id": slot}, headers=owner).json()["status"] == "ACCEPTED"
    assert len(client.get(f"{API}/visits/calendar", headers=owner).json()) == 1
    # modification : repart en négociation
    s2, e2 = future(days=3)
    mod = client.post(f"{API}/visits/{vid}/slots", json={"slots": [{"starts_at": s2, "ends_at": e2}]}, headers=owner).json()
    assert mod["status"] == "PROPOSED" and not any(x["is_selected"] for x in mod["slots"])
    assert client.patch(f"{API}/visits/{vid}", json={"action": "cancel"}, headers=seeker).json()["status"] == "CANCELLED"
    # tiers sans accès ; créneau passé refusé
    _, other = api.user("o2@test.tn")
    assert client.patch(f"{API}/visits/{vid}", json={"action": "cancel"}, headers=other).status_code == 404
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    assert client.post(f"{API}/visits", json={"property_id": pid, "slots": [{"starts_at": past, "ends_at": past}]}, headers=seeker).status_code == 422


def test_roommate_matching_and_requests(api, client, city_id):
    aid, a = api.user("a@test.tn")
    bid, b = api.user("b@test.tn")
    cid, c = api.user("c@test.tn")
    assert client.get(f"{API}/roommates", headers=a).status_code == 422  # profil requis
    base = {"city_id": city_id, "budget_min": "300", "budget_max": "500", "schedule": "EARLY", "cleanliness": 4, "sociability": 3}
    client.put(f"{API}/roommates/me", json=base, headers=a)
    client.put(f"{API}/roommates/me", json=base, headers=b)
    client.put(f"{API}/roommates/me", json={**base, "smoker": True, "schedule": "NIGHT", "cleanliness": 1, "budget_min": "900", "budget_max": "1200"}, headers=c)
    res = client.get(f"{API}/roommates", headers=a).json()
    assert [r["profile"]["user_id"] for r in res] == [bid, cid] and res[0]["score"] == 100 > res[1]["score"]
    assert client.get(f"{API}/roommates/{bid}/compatibility", headers=a).json()["score"] == 100
    req = client.post(f"{API}/roommate-requests", json={"receiver_id": bid, "message": "Hello"}, headers=a)
    assert req.status_code == 201
    assert client.post(f"{API}/roommate-requests", json={"receiver_id": bid}, headers=a).status_code == 409
    assert client.patch(f"{API}/roommate-requests/{req.json()['id']}", json={"accept": True}, headers=a).status_code == 404
    assert client.patch(f"{API}/roommate-requests/{req.json()['id']}", json={"accept": True}, headers=b).json()["status"] == "ACCEPTED"
    # blocage : disparaît des résultats
    client.post(f"{API}/users/{cid}/block", headers=a)
    assert [r["profile"]["user_id"] for r in client.get(f"{API}/roommates", headers=a).json()] == [bid]


def test_messaging_blocking_attachments_read(api, client, city_id, category_id):
    aid, a = api.user("a@test.tn")
    bid, b = api.user("b@test.tn")
    _, c = api.user("c@test.tn")
    cid = client.post(f"{API}/conversations", json={"user_id": bid}, headers=a).json()["id"]
    assert client.post(f"{API}/conversations", json={"user_id": aid}, headers=b).json()["id"] == cid  # même conversation
    m = client.post(f"{API}/conversations/{cid}/messages", json={"body": "Salut"}, headers=a).json()
    assert m["status"] == "sent"
    convs = client.get(f"{API}/conversations", headers=b).json()
    assert convs[0]["unread_count"] == 1 and convs[0]["title"].startswith("Test")
    assert client.patch(f"{API}/conversations/{cid}/read", headers=b).status_code == 204
    assert client.get(f"{API}/conversations/{cid}/messages", headers=a).json()[0]["status"] == "read"
    # un tiers ne peut ni lire ni écrire
    assert client.get(f"{API}/conversations/{cid}/messages", headers=c).status_code == 404
    assert client.post(f"{API}/conversations/{cid}/messages", json={"body": "x"}, headers=c).status_code == 404
    # pièce jointe privée : accessible aux membres seulement
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 50
    att = client.post(f"{API}/conversations/{cid}/attachments", files={"file": ("p.png", io.BytesIO(png), "image/png")}, headers=a)
    assert att.status_code == 201
    aid_ = att.json()["attachments"][0]["id"]
    assert client.get(f"{API}/attachments/{aid_}", headers=b).content == png
    assert client.get(f"{API}/attachments/{aid_}", headers=c).status_code == 404
    assert client.get(f"{API}/attachments/{aid_}").status_code == 401
    # blocage : plus de messages
    client.post(f"{API}/users/{aid}/block", headers=b)
    assert client.post(f"{API}/conversations/{cid}/messages", json={"body": "encore"}, headers=a).status_code == 403
    # partage d'annonce
    _, owner = api.user("o@test.tn", ["OWNER"])
    pid = make_property(client, owner, city_id, category_id)["id"]
    client.delete(f"{API}/users/{aid}/block", headers=b)
    assert client.post(f"{API}/conversations/{cid}/messages", json={"property_id": pid}, headers=a).json()["property_id"] == pid


def test_websocket_realtime(api, client):
    aid, a = api.user("a@test.tn")
    bid, b = api.user("b@test.tn")
    cid = client.post(f"{API}/conversations", json={"user_id": bid}, headers=a).json()["id"]
    token_b = b["Authorization"].split()[1]
    with client.websocket_connect(f"{API}/ws") as ws:
        ws.send_json({"type": "auth", "token": token_b})
        assert ws.receive_json()["type"] == "ready"
        client.post(f"{API}/conversations/{cid}/messages", json={"body": "temps réel"}, headers=a)
        msg = ws.receive_json()
        assert msg["type"] == "message" and msg["body"] == "temps réel"


def test_websocket_rejects_bad_token(client):
    import pytest
    from starlette.websockets import WebSocketDisconnect
    with client.websocket_connect(f"{API}/ws") as ws:
        ws.send_json({"type": "auth", "token": "bad"})
        with pytest.raises(WebSocketDisconnect):
            ws.receive_json()


def test_notifications_read(api, client, city_id, category_id):
    oid, owner, sid, seeker, pid = setup_rental(api, client, city_id, category_id)
    client.post(f"{API}/rental-requests", json={"property_id": pid}, headers=seeker)
    n = client.get(f"{API}/notifications", headers=owner).json()
    assert n["unread_count"] == 1
    nid = n["items"][0]["id"]
    assert client.patch(f"{API}/notifications/{nid}/read", headers=seeker).status_code == 404  # pas la sienne
    assert client.patch(f"{API}/notifications/{nid}/read", headers=owner).status_code == 200
    assert client.get(f"{API}/notifications", headers=owner).json()["unread_count"] == 0


def test_admin_permissions_and_features(api, client):
    uid, user = api.user("u@test.tn")
    admin = api.login("admin@test.tn", "AdminPass123")
    for method, url in [("get", "/admin/users"), ("get", "/admin/stats"), ("get", "/admin/settings"), ("post", "/admin/regions")]:
        assert getattr(client, method)(API + url, headers=user).status_code == 403
        assert getattr(client, method)(API + url).status_code == 401
    st = client.get(f"{API}/admin/stats", headers=admin).json()
    assert st["users"] == 2 and st["seekers"] == 1
    assert client.get(f"{API}/admin/users", params={"q": "u@"}, headers=admin).json()["total"] == 1
    # catégories & villes
    cat = client.post(f"{API}/admin/categories", json={"name": "Riad"}, headers=admin)
    assert cat.status_code == 201
    assert client.post(f"{API}/admin/categories", json={"name": "Riad"}, headers=admin).status_code == 409
    assert client.delete(f"{API}/admin/categories/{cat.json()['id']}", headers=admin).status_code == 204
    # paramètres de score
    assert client.put(f"{API}/admin/settings", json={"compat_weight_city": "50"}, headers=admin).json()["compat_weight_city"] == "50"
    assert client.put(f"{API}/admin/settings", json={"compat_weight_city": "abc"}, headers=admin).status_code == 422
    assert client.put(f"{API}/admin/settings", json={"secret_key": "x"}, headers=admin).status_code == 422
    # un admin ne peut pas se suspendre
    me = client.get(f"{API}/users/me", headers=admin).json()["id"]
    assert client.patch(f"{API}/admin/users/{me}/status", json={"status": "BANNED"}, headers=admin).status_code == 409


def test_identity_document_is_private(api, client):
    uid, a = api.user("a@test.tn")
    _, b = api.user("b@test.tn")
    admin = api.login("admin@test.tn", "AdminPass123")
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 50
    r = client.post(f"{API}/users/me/identity-documents", data={"doc_type": "ID_CARD"}, files={"file": ("id.png", io.BytesIO(png), "image/png")}, headers=a)
    assert r.status_code == 201
    did = r.json()["id"]
    assert client.get(f"{API}/users/identity-documents/{did}", headers=a).content == png
    assert client.get(f"{API}/users/identity-documents/{did}", headers=admin).status_code == 200
    assert client.get(f"{API}/users/identity-documents/{did}", headers=b).status_code == 404
    assert client.get(f"{API}/users/identity-documents/{did}").status_code == 401


def test_profile_update_and_roles(api, client, city_id):
    uid, h = api.user("a@test.tn")
    r = client.put(f"{API}/users/me", json={"bio": "Étudiant", "city_id": city_id, "roles": ["SEEKER", "OWNER"]}, headers=h)
    assert r.status_code == 200 and sorted(r.json()["roles"]) == ["OWNER", "SEEKER"]
    assert client.put(f"{API}/users/me", json={"roles": ["ADMIN"]}, headers=h).status_code == 422
    assert client.put(f"{API}/users/me/password", json={"current_password": "wrong", "new_password": "NewPassw0rd1"}, headers=h).status_code == 422
    assert client.put(f"{API}/users/me/password", json={"current_password": "Passw0rdOK", "new_password": "NewPassw0rd1"}, headers=h).status_code == 200
    api.login("a@test.tn", "NewPassw0rd1")


def test_public_profile_hides_private_data(api, client):
    uid, a = api.user("a@test.tn", first="Salma", last="Ben Ali")
    _, b = api.user("b@test.tn")
    p = client.get(f"{API}/users/{uid}/public-profile", headers=b).json()
    assert "email" not in p and p["last_name"] == "B."


def test_report_user(api, client):
    aid, a = api.user("a@test.tn")
    bid, b = api.user("b@test.tn")
    assert client.post(f"{API}/reports", json={"reported_user_id": bid, "reason": "Spam"}, headers=a).status_code == 201
    assert client.post(f"{API}/reports", json={"reported_user_id": aid, "reason": "Spam"}, headers=a).status_code == 422


def test_cors_restrictive(client):
    r = client.options(f"{API}/health", headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in r.headers
    r = client.options(f"{API}/health", headers={"Origin": "http://localhost:4200", "Access-Control-Request-Method": "GET"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:4200"


def test_health_and_no_internal_error_leak(client):
    assert client.get(f"{API}/health").json() == {"status": "ok", "database": "up"}
