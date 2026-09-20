import urllib.request
import json

test_cases = [
    {
        "id": 1,
        "input": "I have 30 packets of veg biryani made at 7 PM.",
        "checks": lambda r: (
            r.get("food_name") == "Veg Biryani" and
            r.get("quantity") == 30 and
            r.get("unit") in ["packets", "packet"] and
            r.get("food_type") == "vegetarian" and
            r.get("prepared_time") is not None and
            r.get("expiry_time") is None
        )
    },
    {
        "id": 2,
        "input": "50 meals of chicken biryani prepared at 6 PM.",
        "checks": lambda r: (
            r.get("food_name") == "Chicken Biryani" and
            r.get("quantity") == 50 and
            r.get("unit") in ["meals", "meal"] and
            r.get("food_type") == "non_vegetarian" and
            r.get("prepared_time") is not None and
            r.get("expiry_time") is None
        )
    },
    {
        "id": 3,
        "input": "We have 10 kg cooked rice.",
        "checks": lambda r: (
            r.get("food_name") in ["Cooked Rice", "Rice"] and
            r.get("quantity") == 10 and
            r.get("unit") == "kg" and
            r.get("prepared_time") is None and
            r.get("expiry_time") is None
        )
    },
    {
        "id": 4,
        "input": "Some leftover vegetarian food.",
        "checks": lambda r: (
            r.get("food_name") is not None and
            r.get("quantity") is None and
            r.get("food_type") == "vegetarian" and
            r.get("prepared_time") is None and
            r.get("expiry_time") is None
        )
    },
    {
        "id": 5,
        "input": "100 boxes of meals, pickup needed urgently.",
        "checks": lambda r: (
            r.get("quantity") == 100 and
            r.get("unit") == "boxes" and
            r.get("prepared_time") is None and
            r.get("expiry_time") is None
        )
    },
    {
        "id": 6,
        "input": "I have 25 packets of food.",
        "checks": lambda r: (
            r.get("quantity") == 25 and
            r.get("unit") in ["packets", "packet"] and
            r.get("prepared_time") is None and
            r.get("expiry_time") is None
        )
    }
]

url = "http://localhost:8000/api/ai/extract-food"
print(f"Testing endpoint: {url}\n" + "=" * 60)

passed = 0
for tc in test_cases:
    req = urllib.request.Request(
        url,
        data=json.dumps({"description": tc["input"]}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            ok = tc["checks"](data)
            status = "PASS" if ok else "FAIL"
            if ok:
                passed += 1
            print(f"[{status}] Test Case {tc['id']}: '{tc['input']}'")
            print(f"       Extracted: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"[FAIL] Test Case {tc['id']}: Error {e}")

print("=" * 60)
print(f"Result: {passed}/{len(test_cases)} tests passed.")
if passed == len(test_cases):
    print("ALL TEST CASES PASSED SUCCESSFULLY!")
