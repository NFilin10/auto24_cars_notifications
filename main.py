import requests
from bs4 import BeautifulSoup
import psycopg2


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

url = "https://rus.auto24.ee/"

r = requests.get(url, headers=headers)
print(r.headers)
soup = BeautifulSoup(r.content, 'html.parser')


#getting make
def get_make():

    make_div = soup.find('div', {'id' : 'item-searchParam-cmm-1-make'})
    makes = make_div.find_all("option", {"class": "input-option"})
    makes = makes[1:]

    makes_dict = {}

    for option in makes:
        option_text = option.text
        option_value = option['value']
        makes_dict[option_text] = option_value


    return makes_dict



#getting model according make
def get_model(model_id):
    request_model_url = "https://rus.auto24.ee/services/data_json.php?q=models&existonly=true&parent=" + str(model_id) + "&type=100"
    request_model = requests.get(request_model_url, headers=headers)

    models_dict = {}

    model_response = request_model.json()['q']['response']
    for item in model_response:
        if "все" in item['label']:
            pass
        else:
            models_dict[item['label']] = item['value']
        if 'children' in item:
            for child in item['children']:
                models_dict[child['label']] = child['value']
    return models_dict


# for key, value in models_dict.items():
#     print(key, value)


# #getting body type
# body_type_div = soup.find('div', {'id' : 'item-searchParam-bodytype'})
# body_types = body_type_div.find_all("option", {"class": "input-option"})
# body_types = body_types[1:]
#
#
# body_types_dict = {}
#
# for option in body_types:
#     option_text = option.text
#     option_value = option['value']
#     body_types_dict[option_value] = option_text
#
# # for k, v in body_types_dict.items():
# #     print(k, v)
#
#
# #getting fuel
def get_fuel():
    fuel_div = soup.find('div', {'id' : 'item-searchParam-fuel'})
    fuels = fuel_div.find_all("option", {"class": "input-option"})
    fuels = fuels[1:]

    fuels_dict = {}

    for option in fuels:
        option_text = option.text
        option_value = option['value']
        fuels_dict[option_text] = option_value
    return fuels_dict
#
# # for k, v in fuels_dict.items():
# #     print(k, v)
#
#
#
# #getting transm
def get_transm():
    transm_div = soup.find('div', {'id' : 'item-searchParam-transmission'})
    transms = transm_div.find_all("option", {"class": "input-option"})
    transms = transms[1:]

    transms_dict = {}

    for option in transms:
        option_text = option.text
        option_value = option['value']
        transms_dict[option_text] = option_value
    return transms_dict
#
# # for k, v in transms_dict.items():
# #     print(k, v)
#
#
# #getting drivetrain
def get_driv():
    driv_div = soup.find('div', {'id' : 'item-searchParam-drivetrain'})
    drivs = driv_div.find_all("option", {"class": "input-option"})
    drivs = drivs[1:]

    drivs_dict = {}

    for option in drivs:
        option_text = option.text
        option_value = option['value']
        drivs_dict[option_text] = option_value
    return drivs_dict
#
# # for k, v in drivs_dict.items():
# #     print(k, v)
#
#
#
#
# #getting all variants
#
# payload1 = {
# 'bn': '2',
# 'a': '100',
# 'aj': '',
# 'b': '2',
# 'bw': '2056',
# 'ae': '8',
# 'af': '50',
# 'otsi': 'otsi (31785)',
# 'j': ['1', '3'],
#
#
# }
#
#
# request_variants = requests.get("https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&b=2&bw=36&ae=8&af=50&j=1&j=3", data=payload1, headers=headers)
# # print(s.text)
#
#
# soup_variants = BeautifulSoup(request_variants.content, 'html.parser')
#
# #getting number of pages
# pages = soup_variants.find(class_='page-cntr')
# pages = pages.text.strip()
# slash_index = pages.find('/')
# closing_parenthesis_index = pages.find(')')
#
# page_num = pages[slash_index + 1:closing_parenthesis_index]
#
#
# #getting model
#
# for i in range(0, (int(page_num)+1)*50-50, 50):
#     s = requests.get("https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&b=2&bw=36&ae=8&af=50&j=1&j=3&ak=" + "i", data=payload1, headers=headers)
#     div_description = soup_variants.findAll('div', class_='description')
#     for i in div_description:
#         model_heading = i.find(class_='main').text.strip()
#         div_extra = i.find('div', class_='extra')
#         year_span = div_extra.select('span.year')
#         mileage_span = div_extra.select('span.mileage')
#         fuel_span = div_extra.select('span.fuel')
#         transmission_span = div_extra.select('span.transmission')
#         bodytype_span = div_extra.select('span.bodytype')
#         drive_span = div_extra.select('span.drive')
#         try:
#             print(model_heading)
#             print(year_span[0].text)
#             print(mileage_span[0].text)
#             print(fuel_span[0].text)
#             print(transmission_span[0].text)
#             print(bodytype_span[0].text)
#             print(drive_span[0].text)
#             print("#############################")
#         except:
#             pass
#
#
#
# #DBCONNECTION
#
# conn = psycopg2.connect(database="car_models",
#                         host="localhost",
#                         user="nikita_filin",
#                         password="9112",
#                         port="5432")
#
# cursor = conn.cursor()

# https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&aj=&ssid=103455360&j%5B%5D=1&j%5B%5D=2&b=2&bw=36&f1=2004&f2=2012&g1=1000&g2=10000&h%5B%5D=1&i%5B%5D=1&p%5B%5D=1&ae=8&af=50&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA
#https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&b=2&bw=36&ae=8&af=50