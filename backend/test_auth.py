from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- Test Login with correct password ---")
res = client.post("/auth/login", json={"password": "abc"})
print("Status:", res.status_code)
print("Set-Cookie Header:", res.headers.get("set-cookie"))

print("\n--- Test Login with wrong password ---")
res = client.post("/auth/login", json={"password": "wrong"})
print("Status:", res.status_code)
print("Response:", res.json())

print("\n--- Test Protected Route without Cookie ---")
res = client.get("/products/")
print("Status:", res.status_code)
print("Response:", res.json())

print("\n--- Test Protected Route with correct Cookie ---")
# Using the test client to set the cookie
client.cookies.set("avocado_auth_token", "authenticated_user_abc")
res = client.get("/products/")
print("Status:", res.status_code)
# We don't print the whole JSON as it might be large
print("Response keys (or error):", list(res.json().keys()) if isinstance(res.json(), dict) else "List of items")
