import requests
from   datetime import datetime, timedelta, timezone
from   dotenv   import load_dotenv; load_dotenv()
import json
import os

# Credit : This script was assisted with AI tools
# ---
# Step 0: Connections / API / Keys
# This step is ommited for privacy 
# ---


# -------------------------------------------------------
# STEP 1: Exchange auth code for tokens (run this ONCE)
# After you get your refresh token, you won't need this again
# -------------------------------------------------------
def exchange_code_for_tokens(auth_code):
    print("Exchanging auth code for tokens...")
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code":          auth_code,
            "grant_type":    "authorization_code"
        }
    )
    result = response.json()
 
    if "access_token" not in result:
        print("ERROR:", result)
        return
 
    print("\n Success! Save these values:\n")
    print(f"  ACCESS_TOKEN:  {result['access_token']}")
    print(f"  REFRESH_TOKEN: {result['refresh_token']}")
    print(f"  Expires at:    {result['expires_at']}")
    print("\nCopy your REFRESH_TOKEN into the REFRESH_TOKEN variable above.")
    return result
 
 
# -------------------------------------------------------
# STEP 2: Get a fresh access token using your refresh token
# (access tokens expire every 6 hours, this handles that)
# -------------------------------------------------------
def get_access_token():
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type":    "refresh_token"
        }
    )
    result = response.json()
 
    if "access_token" not in result:
        print("ERROR refreshing token:", result)
        return None
 
    print(f" Got fresh access token (expires at {result['expires_at']})")
    return result["access_token"]
 
 
# -------------------------------------------------------
# STEP 3: Fetch all your activities from Strava
# -------------------------------------------------------
def fetch_all_activities(access_token, weeks_back=2):
    cutoff = datetime.now(timezone.utc) - timedelta(weeks=weeks_back)
    cutoff_timestamp = int(cutoff.timestamp())

    print("\nFetching activities...")
    activities = []
    page = 1
 
    while True:
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "per_page": 200, 
                "page"    : page,
                "after"   : cutoff_timestamp
            }
        )
        batch = response.json()
 
        if not batch:
            break
 
        print(f"  Page {page}: got {len(batch)} activities")
        activities.extend(batch)
        page += 1
 
    print(f"\n Total activities fetched: {len(activities)}")
    return activities
 
 
# -------------------------------------------------------
# STEP 4: Save data to a JSON file
# -------------------------------------------------------
def save_to_file(activities, filename="activities.json"):
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", filename)
 
    with open(filepath, "w") as f:
        json.dump(activities, f, indent=2)
 
    print(f" Saved to {filepath}")
    return filepath
 
 
# -------------------------------------------------------
# MAIN — control what runs here
# -------------------------------------------------------
if __name__ == "__main__":
 
    # --- FIRST TIME ONLY ---
    # Uncomment the 3 lines below, fill in your AUTH_CODE, and run once.
    # Then copy the refresh token printed, paste it above, and comment these out again.
 
    # tokens = exchange_code_for_tokens(AUTH_CODE)
    # if not tokens:
    #     exit()
 
 
    # --- NORMAL SYNC (run this every time after first setup) ---
    access_token = get_access_token()
 
    if access_token:
        activities = fetch_all_activities(access_token, weeks_back=3)
        save_to_file(activities)
