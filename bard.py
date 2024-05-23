from gemini import Gemini

import browser_cookie3
import requests
import os

# chromecookies = os.path.join(os.path.expandvars("%userprofile%"),"AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies")
# cookiejar = browser_cookie3.chrome(cookie_file=chromecookies, domain_name="google.com")
# print(cookiejar)

client = Gemini(auto_cookies=True)

# Testing needed as cookies vary by region.
# client = Gemini(auto_cookies=True, target_cookies=["__Secure-1PSID", "__Secure-1PSIDTS"])
# client = Gemini(auto_cookies=True, target_cookies="all") # You can pass whole cookies

response = client.generate_content("me explica ia ai meu jovem")
print(response.payload)