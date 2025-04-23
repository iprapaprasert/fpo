import http.client
import json
import pandas as pd

conn = http.client.HTTPSConnection("apigw1.bot.or.th")

headers = {
    'X-IBM-Client-Id': "d2ee985e-51c5-4e56-81b3-0bd5dc983e02",
    'accept': "application/json"
    }

conn.request("GET", "/bot/public/categorylist/series_list/?category=EC_EI_003_S3", headers=headers)

res = conn.getresponse()
data = res.read().decode("utf-8")

# Extract and transform the data
response_data = json.loads(data)
series_data = response_data["result"]["series"]
df = pd.DataFrame([{
    "series_name_eng": item["series_name_eng"].strip(),
    "series_name_thai": item["series_name_th"].strip(),
    "series_code": item["series_code"]
} for item in series_data])

# Display or export
df.to_excel("Z:/databank/Consumption/bot_pci_series_code.xlsx", index=False)
