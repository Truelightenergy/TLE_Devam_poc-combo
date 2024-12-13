# prod server

# import requests
# def login(email, password):
#     url = "https://truepriceenergy.com/login"
#     querystring = {"email":email,"password":password}
#     response = requests.request("GET", url, params=querystring, verify=False)
#     return response.text

# def download_data(access_token, start_date, end_date, operating_day, offset, curve, iso, strip, history, type):
#     url = "https://truepriceenergy.com/get_data"
#     querystring = {
#         "start": start_date,
#         "end": end_date,
#         "curve_type": curve,
#         "iso": iso,
#         "strip": strip,
#         "history": history,
#         "type": type
#     }
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(url, params=querystring, headers=headers, verify=False)

#     with open(f"{curve}_{iso}.csv", "wb") as file:
#         file.write(response.content)

#     return response


# access_token = eval(login("anwar@truelightenergy.com", "anwar@truelightenergy.com"))["access_token"]

# data = download_data(access_token, "2024-12-01", "2029-12-01", "2024-11-21", "0", "nonenergy", "ercot",['7x8', '5x16', '2x16'], False, "csv")



# dev server
import requests
import os
from tqdm import tqdm 

def login(email, password):
    url = "http://3.21.123.23:8011/login"
    querystring = {"email": email, "password": password}
    response = requests.get(url, params=querystring, verify=False)
    return response.text

def get_data(access_token, start_date, end_date, operating_day, operating_day_end, curve, iso, strip, idcob, type):
    url = "http://3.21.123.23:8011/get_data"
    querystring = {
        "start": start_date,
        "end": end_date,
        "curve_type": curve,
        "iso": iso,
        "strip": strip,
        "idcob": idcob,
        "type": type,
        "operating_day": operating_day,
        "operating_day_end": operating_day_end
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, params=querystring, headers=headers, verify=False)
    
    base_path = os.path.abspath(os.getcwd()) 
    folder_path = os.path.join(base_path, "Dev_Testing") 
    os.makedirs(folder_path, exist_ok=True)  
    
    file_path = os.path.join(folder_path, f"{curve}_{iso}_{strip}_{operating_day}_dev.csv")
    with open(file_path, "wb") as file:
        file.write(response.content)
    # print(f"Data saved to {file_path}")
    return response


access_token = eval(login("anwar@truelightenergy.com", "anwar@truelightenergy.com"))["access_token"]


# curves = ["energy", "nonenergy", "rec", "ptc", "matrix_pricing"]
isos = ["ercot", "isone", "nyiso", "miso", "pjm"]
strips = ["standardized", "unstandardized"]

# if access_token:
#     for curve in tqdm(curves, desc="Processing curves"):
#         for iso in isos:
#             for strip in strips:
#                 print(f"Downloading data for curve: {curve}, iso: {iso}, strip: {strip}")
#                 get_data(
#                     access_token,
#                     "2024-01-01",
#                     "9999-12-31",
#                     "","",  
#                     curve,
#                     iso,
#                     strip,
#                     "latestall",
#                     "csv"
#                 )
# else:
#     print("No access token. Exiting.")

# if(access_token):
#     for iso in tqdm(isos, desc="Processing curves"):
#         for strip in strips:
#             get_data(access_token, "2024-02-01", "2029-02-01", "2024-01-15","2024-01-15", "ptc", iso, strip, "latestall", "csv")


# ptc ercot
# if(access_token):
#     with tqdm(total=len(strips), desc="Downloading data") as pbar:
#         for strip in strips:
#             get_data(access_token, "2024-02-01", "2029-02-01", "","", "ptc", "ercot", strip, "latestall", "csv")


# matrix pricing

# if(access_token):
#     with tqdm(total=(len(isos)*len(strips)), desc="Downloading data") as pbar:
#         for iso in isos:
#             for strip in strips:
#                 get_data(access_token, "2024-10-01", "2029-10-01", "2024-09-30","2024-09-30", "matrix", iso, strip, "latestall", "csv")
#                 pbar.update(1)


# non energy 

# if(access_token):
#     with tqdm(total=(len(isos)*len(strips)), desc="Downloading data") as pbar:
#         for iso in isos:
#             for strip in strips:
#                 get_data(access_token, "2024-02-01", "2029-02-01", "2024-01-05","2024-01-05", "nonenergy", iso, strip, "latestall", "csv")
#                 pbar.update(1)

# non energy pjm
# if(access_token):
#     with tqdm(total=len(strips), desc="Downloading data") as pbar:
#         for strip in strips:
#                 get_data(access_token, "2024-02-01", "2029-02-01", "2024-01-31","2024-01-31", "nonenergy", "pjm", strip, "latestall", "csv")
#                 pbar.update(1)


# non energy miso
if(access_token):
    with tqdm(total=len(strips), desc="Downloading data") as pbar:
        for strip in strips:
                get_data(access_token, "2024-10-01", "2029-10-01", "2024-09-30","2024-10-30", "nonenergy", "miso", strip, "latestall", "csv")
                pbar.update(1)


# energy 

# if(access_token):
#     with tqdm(total=len(strips), desc="Downloading data") as pbar:
#         for strip in strips:
#             for iso in isos:
#                 get_data(access_token, "2024-02-01", "2029-02-01", "2024-01-02","2024-01-02", "energy", iso, strip, "latestall", "csv")
#                 pbar.update(1)

