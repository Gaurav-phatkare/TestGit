import requests
import json
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────

BASE_URL = "http://72.61.243.37:6112"

PAYLOAD = {
    "question": "total number of answers available for respective slp questions along with question id and actual question",
    # "pinned_tables": ["appfinaldata", "slp_questions"],  # uncomment to pin tables
    # "max_retries": 5                                      # uncomment to override retries
}

# ─────────────────────────────────────────────────────────────────
# Call /query
# ─────────────────────────────────────────────────────────────────

print(f"Calling POST {BASE_URL}/query ...")
print(f"Payload: {json.dumps(PAYLOAD, indent=2)}\n")

try:
    response = requests.post(
        url     = f"{BASE_URL}/query",
        headers = {"Content-Type": "application/json"},
        json    = PAYLOAD,
        timeout = 120,
    )

    print(f"Status Code : {response.status_code}")
    print(f"Response Time: {response.elapsed.total_seconds():.2f}s\n")

    data = response.json()

    # ── Save to file ──────────────────────────────────────────────
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"query_response_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"Response saved to: {output_file}")

    # ── Quick summary ─────────────────────────────────────────────
    print("\n── Summary ──────────────────────────────────────────")
    print(f"Status       : {data.get('status')}")

    if data.get("status") == "success":
        print(f"SQL          : {data.get('sql', '')[:120]}...")
        print(f"Rows         : {data.get('rows')}")
        print(f"Columns      : {data.get('columns')}")
        print(f"Tables Used  : {data.get('tables_used')}")
        print(f"Attempts     : {data.get('attempts')}")
        print(f"Reasoning    : {data.get('reasoning', '')[:200]}")
        print(f"Chart Type   : {data.get('visualization', {}).get('chart_type')}")
        print(f"Output CSV   : {data.get('output_csv')}")

        print("\n── First 3 Rows ──────────────────────────────────────")
        for row in data.get("data", [])[:3]:
            print(row)
    else:
        print(f"Error        : {data.get('message')}")
        print(f"Details      : {data.get('details')}")
        print(f"\nHistory:")
        for h in data.get("history", []):
            print(f"  Attempt {h['attempt']}: valid={h['valid']}, error={h['error']}")

except requests.exceptions.ConnectionError:
    print(f"ERROR: Could not connect to {BASE_URL}. Is the server running?")
except requests.exceptions.Timeout:
    print("ERROR: Request timed out after 120s.")
except Exception as e:
    print(f"ERROR: {e}")
