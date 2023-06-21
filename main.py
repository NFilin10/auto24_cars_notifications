import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import sql
from cfg import cursor, conn
import logging

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

url = "https://rus.auto24.ee/"

r = requests.get(url, headers=headers)
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
def get_body_type():
    body_type_div = soup.find('div', {'id' : 'item-searchParam-bodytype'})
    body_types = body_type_div.find_all("option", {"class": "input-option"})
    body_types = body_types[1:]


    body_types_dict = {}

    counter = 0

    for option in body_types:
        if counter == 8:
            break
        option_text = option.text
        option_value = option['value']
        body_types_dict[option_text] = option_value
        counter+=1

    return body_types_dict
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
def request(payload, url, short_model, make_id, table_status):
    found_models = []
    print("doing request function")


    request_variants = requests.get(url, data=payload, headers=headers)
    # print(s.text)


    soup_variants = BeautifulSoup(request_variants.content, 'html.parser')

    #getting number of pages
    pages = soup_variants.find(class_='page-cntr')
    if pages is None:
        return -1


    pages = pages.text.strip()
    slash_index = pages.find('/')
    closing_parenthesis_index = pages.find(')')

    page_num = pages[slash_index + 1:closing_parenthesis_index]


    #getting model

    for i in range(0, (int(page_num)+1)*100-100, 100):
        s = requests.get(url + "&ak=" + str(i), data=payload, headers=headers)
        soup_variant_page = BeautifulSoup(s.content, 'html.parser')
        a_link = [a['href'] for a in soup_variant_page.find_all('a', class_='row-link')]
        div_description = soup_variant_page.findAll('div', class_='description')
        for i, j in zip(div_description, a_link):
            model_heading = i.find(class_='main')

            make = model_heading.find('span')
            if make is not None:
                make = make.text
            else:
                make = ""

            model = model_heading.find('span', class_='model')

            if model is not None:
                model = model.text
            else:
                model = ""



            engine = model_heading.find('span', class_='engine')
            if engine is not None:
                engine = engine.text
            else:
                engine = ""

            price_block = i.find('span', class_='price')
            price = price_block.text


            model_heading = make + " " + model + " " + engine


            year_span = i.find_all('span', class_='year')
            if year_span:
                year = year_span[0].text
            else:
                year = None


            mileage_span = i.find_all('span', class_='mileage')
            if mileage_span:
                mileage = mileage_span[0].text
            else:
                mileage = None

            fuel_span = i.find_all('span', class_='fuel')
            if fuel_span:
                fuel = fuel_span[0].text
            else:
                fuel = None

            transmission_span = i.find_all('span', class_='transmission')
            if transmission_span:
                transmission = transmission_span[0].text
            else:
                transmission = None

            bodytype_span = i.find_all('span', class_='bodytype')
            if bodytype_span:
                bodytype = bodytype_span[0].text
            else:
                bodytype = None

            drive_span = i.find_all('span', class_='drive')
            if drive_span:
                drive = drive_span[0].text
            else:
                drive = None

            link = j

            if table_status == 1:
                print("TABLE STATUS 1")
                sql_no_rows(model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link, make_id)

            elif table_status == 2:
                print("TABLE STATUS 2")
                sql_rows_and_new_model(model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link, make_id)

            elif table_status == 3:
                print("TABLE STATUS 3")
                sql_rows_and_model(model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link, make_id)

            elif table_status == 4:
                print("TABLE STATUS 4")
                result = sql_searching(model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link, make_id)
                if result is not None:
                    found_models.append(result)
    return found_models







def sql_no_rows(model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link, make_id):

        cursor.execute(
            sql.SQL(
                "INSERT INTO {} (model, model_short, year, mileage, fuel, transm, body_type, drive, price, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                .format(sql.Identifier(make_id)),
            (model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link)
        )
        conn.commit()


def sql_rows_and_new_model(model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link, make_id):
    cursor.execute(
        sql.SQL(
            "INSERT INTO {} (model, model_short, year, mileage, fuel, transm, body_type, drive, price, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            .format(sql.Identifier(make_id)),
        (model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link)
    )
    conn.commit()


def sql_rows_and_model(model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link, make_id):

    cursor.execute(sql.SQL("SELECT EXISTS(SELECT 1 FROM {} WHERE link = %s)").format(sql.Identifier(make_id)), (link,)
                   )
    exists = cursor.fetchone()[0]

    if not exists:
        cursor.execute(
            sql.SQL(
                "INSERT INTO {} (model, model_short, year, mileage, fuel, transm, body_type, drive, price, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                .format(sql.Identifier(make_id)),
            (model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link)
        )
        conn.commit()


def sql_searching(model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link, make_id):

    cursor.execute(sql.SQL("SELECT EXISTS(SELECT 1 FROM {} WHERE link = %s)").format(sql.Identifier(make_id)), (link,)
                   )
    exists = cursor.fetchone()[0]

    if not exists:
        cursor.execute(
            sql.SQL(
                "INSERT INTO {} (model, model_short, year, mileage, fuel, transm, body_type, drive, price, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                .format(sql.Identifier(make_id)),
            (model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link)
        )
        conn.commit()
        return [model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link]

    return None















# def second_request(payload, url, short_model, make_id):
#     print("creting second request")
#
#     request_variants = requests.get(url, data=payload, headers=headers)
#     # print(s.text)
#
#
#     soup_variants = BeautifulSoup(request_variants.content, 'html.parser')
#
#     #getting number of pages
#     pages = soup_variants.find(class_='page-cntr')
#     if pages is None:
#         return -1
#
#
#     pages = pages.text.strip()
#     slash_index = pages.find('/')
#     closing_parenthesis_index = pages.find(')')
#
#     page_num = pages[slash_index + 1:closing_parenthesis_index]
#
#
#     #getting model
#
#     for i in range(0, (int(page_num)+1)*50-50, 50):
#         s = requests.get(url + "&ak=" + str(i), data=payload, headers=headers)
#         print("SECOND REQUESR --> PAGE URL: " + url + "&ak=" + str(i))
#         soup_variant_page = BeautifulSoup(s.content, 'html.parser')
#
#         div_description = soup_variant_page.findAll('div', class_='description')
#         a_link = [a['href'] for a in soup_variant_page.find_all('a', class_='row-link')]
#
#         for i, j in zip(div_description, a_link):
#
#
#             model_heading = i.find(class_='main')
#
#             make = model_heading.find('span')
#             if make is not None:
#                 make = make.text
#             else:
#                 make = ""
#
#             model = model_heading.find('span', class_='model')
#
#             if model is not None:
#                 model = model.text
#             else:
#                 model = ""
#
#
#
#             engine = model_heading.find('span', class_='engine')
#             if engine is not None:
#                 engine = engine.text
#             else:
#                 engine = ""
#
#             price_block = i.find('span', class_='price')
#             price = price_block.text
#
#
#             model_heading = make + " " + model + " " + engine
#
#
#             year_span = i.find_all('span', class_='year')
#             if year_span:
#                 year = year_span[0].text
#             else:
#                 year = None
#
#
#             mileage_span = i.find_all('span', class_='mileage')
#             if mileage_span:
#                 mileage = mileage_span[0].text
#             else:
#                 mileage = None
#
#             fuel_span = i.find_all('span', class_='fuel')
#             if fuel_span:
#                 fuel = fuel_span[0].text
#             else:
#                 fuel = None
#
#             transmission_span = i.find_all('span', class_='transmission')
#             if transmission_span:
#                 transmission = transmission_span[0].text
#             else:
#                 transmission = None
#
#             bodytype_span = i.find_all('span', class_='bodytype')
#             if bodytype_span:
#                 bodytype = bodytype_span[0].text
#             else:
#                 bodytype = None
#
#             drive_span = i.find_all('span', class_='drive')
#             if drive_span:
#                 drive = drive_span[0].text
#             else:
#                 drive = None
#
#             link = j
#
#
#
#             cursor.execute(sql.SQL("SELECT EXISTS(SELECT 1 FROM {} WHERE link = %s)").format(sql.Identifier(make_id)),(link,)
#             )
#             exists = cursor.fetchone()[0]
#
#             if not exists:
#                 logging.warning("not exists")
#                 logging.warning(f"NEW MODEL: {model}, {short_model}, {year}, {mileage}, {fuel}, {transmission}, {bodytype}, {drive}, {price}, {link}")
#
#
#                 cursor.execute(
#                     sql.SQL(
#                         "INSERT INTO {} (model, model_short, year, mileage, fuel, transm, body_type, drive, price, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
#                         .format(sql.Identifier(make_id)),
#                     (model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link)
#                 )
#                 conn.commit()
#                 return [True, model, short_model, year, mileage, fuel, transmission, bodytype, drive, price, link]
#
#
#     return [False]
#
#
#
