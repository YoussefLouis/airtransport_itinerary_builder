import requests, json

# headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        #    'content-type': 'application/json'}

# fr24_headers = {"authority": "www.flightradar24.com",
#             "method": "GET",
#             "path": "/data/airlines/np-nia/routes?get-airport-arr-dep=CAI",
#             "accept": "application/json",
#             "content-type": "application/json",
#             "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
#         }

myProxy = {"http"  : "http://104.18.72.214:443", "https": "https://104.18.72.214:443"}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0"}


airlines = [
    "ms-msr"
]

egypt_airports  = [
    'SPX',
    'AUE',
    'ABS',
    'ALY',
    'HBE', 
    'ATZ', 
    'ASW', 
    'CAI', 
    'DAK', 
    'AAC', 
    'DBB', 
    'EGH', 
    'UVL', 
    'ELT', 
    'HRG', 
    'LXR', 
    'RMF', 
    'MUH',
    'CCE', 
    'PSD', 
    'GSQ', 
    'SSH', 
    'HMB', 
    'SKV', 
    'TCP'
]


url = "https://www.flightradar24.com/data/airlines/np-nia/routes"

s = requests.Session()

s.get(url, headers=headers)
r = s.post(url, proxies = myProxy, headers=headers, data={"get-airport-arr-dep": "CAI"})
print(r.json())
my_json = json.loads(r.text.split('arrRoutes=')[-1].split(', arrDates=')[0])

print(my_json)

# for airline in airlines: 
    # flightradar_url = "https://www.flightradar24.com/data/airlines/" + airline + "/routes"
    
    # for airport in egypt_airports:
        
    #     payload = {"get-airport-arr-dep": airline}
        
    #     r = requests.get(flightradar_url, headers=headers)
        
    #     print(r.json)

    