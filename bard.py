from gemini import Gemini
import json

cookies = {
    "__Secure-1PSIDCC" : "AKEyXzWWyD2QoZD7gMjfr8twRTbQAcHGgAyNJG7K-nXc0eftNW6rpBW0pLeI5I-F60V0R-APVyQ",
    "__Secure-1PSID" : "g.a000jwhoks05LybkbU5206a5lRXmSEUeV-UHIb1XIUIh21ygjxU3p6wj7L21dM4vE1KrsV8cvQACgYKAU8SAQASFQHGX2Miz_SoQszG7mep2FG3B8jyTxoVAUF8yKpEnmGmyI0oryi0d-cFgPYM0076",
    "__Secure-1PSIDTS" : "sidts-CjIBLwcBXMAh_Pv6RV_lIgAjiKO36rQOy743nMu2Z8JSkJ26W2ByWiSZgpmGp_LBgBi-BxAA",
    "NID" : "514=x7EUAL-4fzQBlIoiAmTRdH5GVhNwLb36f7pwQNsDD7RQFzHcXCaOZuw2uRMbu2OS9PDjlEyxwtKhCL3vreRLbCLDh5SxkJSCtjtE52wbwalXQjOrhXS31Xb82CIT5tkeQiMlOSvry0puPvb4ka12WtQpuHn_QthtUwkZw9Pv7LXicacs0ljJxLmVa4xTj9aBFgNJPTeWdzvpVEz4POq01j1iFmvJUgY7sHDozbi76jcugo1rcjZt90Lj2tCT57umoPyyrT46AqlYIEoaqOmoV9i-TyElgmHvqZcjOYB_iOOymtJz23bAKaYuIlgi7g8zynwE0H_lScHSZJekcFCVhrU7Qu-5Sb_yQBd4IhEdVCxA1IRTJKMlt1QxAu4alcT-2KoaQNI6bM6EIg0iCL0TVY5xuZeHeoABCB4RJrq0eA",
    # Cookies may vary by account or region. Consider sending the entire cookie file.
  }
client = Gemini(cookies=cookies) # You can use various args

response = client.generate_content("oi, vc me entende?")
# response_json = json.loads(response.payload)
print(response.candidates[0].text)