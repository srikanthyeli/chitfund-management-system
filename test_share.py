import asyncio
import urllib.request
import json

async def main():
    # Login to get token
    login_url = "http://127.0.0.1:8000/api/v1/auth/login"
    login_data = json.dumps({"mobile": "1234567890", "password": "I*3Mx5^V*0AC"}).encode()
    
    req = urllib.request.Request(login_url, data=login_data, method="POST")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            token = res_data['access_token']
    except urllib.error.HTTPError as e:
        print("Login failed:", e.code, e.read().decode())
        return

    # Now make the share request
    url = "http://127.0.0.1:8000/api/v1/winner-payouts/bb68f3a2-41e3-4c33-a18e-a3d1dbe82d22/share"
    
    req2 = urllib.request.Request(url, method="POST")
    req2.add_header("Authorization", f"Bearer {token}")
    req2.add_header("Content-Length", "0")
    
    try:
        with urllib.request.urlopen(req2) as response:
            print("Status:", response.status)
            print("Body:", response.read().decode())
    except urllib.error.HTTPError as e:
        print("Status:", e.code)
        print("Body:", e.read().decode())

if __name__ == "__main__":
    asyncio.run(main())
