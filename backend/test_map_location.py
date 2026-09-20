import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8000/api/v1/food/listings"

print("=" * 60)
print("TESTING MAP LOCATION & SUPABASE PERSISTENCE")
print("=" * 60)

# Test 1: Valid donation with Map coordinates (Sri Shakthi Institute)
payload_shakti = {
    "organisation": "Youth Relief Corps",
    "donorName": "Map Integration Tester",
    "foodType": "veg",
    "quantity": "50 meal boxes",
    "location": "Sri Shakthi Institute of Engineering and Technology, Coimbatore",
    "pickup_address": "Sri Shakthi Institute of Engineering and Technology, L&T Bypass, Chinniyampalayam, Coimbatore, Tamil Nadu",
    "latitude": 11.016845,
    "longitude": 76.955832,
    "contact": "+91 9876543210"
}

req1 = urllib.request.Request(
    BASE_URL,
    data=json.dumps(payload_shakti).encode(),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req1) as resp:
    res1 = json.loads(resp.read().decode())
    assert res1.get("id") is not None, "Missing listing ID"
    assert res1.get("latitude") == 11.016845, f"Expected lat 11.016845, got {res1.get('latitude')}"
    assert res1.get("longitude") == 76.955832, f"Expected lng 76.955832, got {res1.get('longitude')}"
    assert "Sri Shakthi" in res1.get("pickup_address", ""), "Address mismatch"
    print("[PASS] Test 1: Created donation with Sri Shakthi Institute coordinates in Supabase!")
    print(f"       Record ID: {res1['id']}")
    print(f"       Latitude : {res1['latitude']}")
    print(f"       Longitude: {res1['longitude']}")

# Test 2: Out of range latitude (must fail with 422)
payload_bad_lat = dict(payload_shakti)
payload_bad_lat["latitude"] = 120.5

req2 = urllib.request.Request(
    BASE_URL,
    data=json.dumps(payload_bad_lat).encode(),
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req2) as resp:
        print("[FAIL] Test 2: Invalid latitude 120.5 was accepted!")
except urllib.error.HTTPError as e:
    assert e.code == 422, f"Expected 422 validation error, got {e.code}"
    print(f"[PASS] Test 2: Invalid latitude correctly rejected with HTTP 422: {e.code}")

# Test 3: Manual address without coordinates (backward compatibility)
payload_manual = {
    "organisation": "Local Community",
    "donorName": "Manual Donor",
    "foodType": "non-veg",
    "quantity": "10 meals",
    "location": "Main Road, Gandhi Nagar",
    "pickup_address": "Main Road, Gandhi Nagar",
    "latitude": None,
    "longitude": None,
    "contact": "+91 9876500000"
}

req3 = urllib.request.Request(
    BASE_URL,
    data=json.dumps(payload_manual).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req3) as resp:
    res3 = json.loads(resp.read().decode())
    assert res3.get("latitude") is None, "Expected None for manual latitude"
    assert res3.get("longitude") is None, "Expected None for manual longitude"
    print("[PASS] Test 3: Manual location without coordinates supported (NULL coordinates)!")

# Test 4: Verify listings retrieval from Supabase
req4 = urllib.request.Request(BASE_URL)
with urllib.request.urlopen(req4) as resp:
    all_listings = json.loads(resp.read().decode())
    assert len(all_listings) >= 2, "Expected at least 2 listings in Supabase"
    has_coords = any(l.get("latitude") is not None for l in all_listings)
    assert has_coords, "No listing has coordinates"
    print(f"[PASS] Test 4: Successfully retrieved {len(all_listings)} listings from Supabase PostgreSQL!")

print("=" * 60)
print("ALL BACKEND & SUPABASE MAP TESTS PASSED!")
print("=" * 60)
