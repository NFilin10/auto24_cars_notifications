import requests
from bs4 import BeautifulSoup


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

url = "https://rus.auto24.ee/"

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.content, 'html.parser')

#getting make
make_div = soup.find('div', {'id' : 'item-searchParam-cmm-1-make'})
makes = make_div.find_all("option", {"class": "input-option"})
makes = makes[1:]

makes_dict = {}

for option in makes:
    option_text = option.text
    option_value = option['value']
    makes_dict[option_value] = option_text


# for key, value in makes_dict.items():
#     print(key, value)

#getting model according make
model_id = 4
request_model_url = "https://rus.auto24.ee/services/data_json.php?q=models&existonly=true&parent=" + str(model_id) + "&type=100"
request_model = requests.get(request_model_url, headers=headers)

models_dict = {}

model_response = request_model.json()['q']['response']
for item in model_response:
    if "все" in item['label']:
        pass
    else:
        models_dict[item['value']] = item['label']
    if 'children' in item:
        for child in item['children']:
            models_dict[child['value']] = child['label']


# for key, value in models_dict.items():
#     print(key, value)


#getting body type
body_type_div = soup.find('div', {'id' : 'item-searchParam-bodytype'})
body_types = body_type_div.find_all("option", {"class": "input-option"})
body_types = body_types[1:]


body_types_dict = {}

for option in body_types:
    option_text = option.text
    option_value = option['value']
    body_types_dict[option_value] = option_text

# for k, v in body_types_dict.items():
#     print(k, v)


#getting fuel
fuel_div = soup.find('div', {'id' : 'item-searchParam-fuel'})
fuels = fuel_div.find_all("option", {"class": "input-option"})
fuels = fuels[1:]

fuels_dict = {}

for option in fuels:
    option_text = option.text
    option_value = option['value']
    fuels_dict[option_value] = option_text

# for k, v in fuels_dict.items():
#     print(k, v)



#getting transm
transm_div = soup.find('div', {'id' : 'item-searchParam-transmission'})
transms = transm_div.find_all("option", {"class": "input-option"})
transms = transms[1:]

transms_dict = {}

for option in transms:
    option_text = option.text
    option_value = option['value']
    transms_dict[option_value] = option_text

# for k, v in transms_dict.items():
#     print(k, v)


#getting drivetrain
driv_div = soup.find('div', {'id' : 'item-searchParam-drivetrain'})
drivs = driv_div.find_all("option", {"class": "input-option"})
drivs = drivs[1:]

drivs_dict = {}

for option in drivs:
    option_text = option.text
    option_value = option['value']
    drivs_dict[option_value] = option_text

for k, v in drivs_dict.items():
    print(k, v)