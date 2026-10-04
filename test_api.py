import os
if os.path.exists("app.db"):
    os.remove("app.db")
from fastapi.testclient import TestClient
from main import app

with TestClient(app) as c:
    def login(u, p):
        r = c.post("/auth/login", data={"username": u, "password": p})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    admin = login("admin", "admin123")
    assert c.post("/auth/register", json={"username": "bob", "password": "secret1"}).status_code == 201
    assert c.post("/auth/register", json={"username": "bob", "password": "secret1"}).status_code == 409
    bob = login("bob", "secret1")

    assert c.get("/items/").status_code == 401                                           # no token
    assert c.post("/items/", json={"name": "A", "price": 5}, headers=bob).status_code == 403  # user can't create
    assert c.patch("/users/2/role", json={"role": "editor"}, headers=admin).json()["role"] == "editor"
    bob = login("bob", "secret1")
    r = c.post("/items/", json={"name": "Laptop", "price": 999.9}, headers=bob)
    assert r.status_code == 201; iid = r.json()["id"]
    assert c.get("/items/?search=lap", headers=bob).json()[0]["name"] == "Laptop"
    assert c.put(f"/items/{iid}", json={"price": 899}, headers=bob).json()["price"] == 899
    assert c.delete(f"/items/{iid}", headers=bob).status_code == 403                     # editor can't delete
    assert c.get("/users/", headers=bob).status_code == 403
    assert c.delete(f"/items/{iid}", headers=admin).status_code == 204
    assert c.get(f"/items/{iid}", headers=admin).status_code == 404
    print("ALL TESTS PASSED")
