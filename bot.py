import time

import telebot
from cfg import bot_token, cursor, conn
import keyboard
import main
from psycopg2 import sql
import logging



bot = telebot.TeleBot(bot_token)

searched_cars = []
interested_models = {}


@bot.message_handler(commands=['add'])
def start(message):
    makes = main.get_make()
    bot.send_message(message.chat.id, "Выберите марку машины или введите вручную", reply_markup=keyboard.make(makes))
    bot.register_next_step_handler(message, get_user_make, makes)


def get_user_make(message, makes):
    make = message.text


    car_info = {}

    if make.capitalize() not in makes and make.upper() not in makes:
        print("error")
    else:
        if make.capitalize() in makes:
            make = make.capitalize()
        elif make.upper() in makes:
            make = make.upper()

        make_id = makes[make]
        print("MAKE ID: " + make_id)
        cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name = %s)", (make_id,))

        if not cursor.fetchone()[0]:
            print("CREATING TABLE FOR MAKE " + make_id)
            cursor.execute(sql.SQL(
                "CREATE TABLE {} (id serial primary key, model varchar(120), model_short varchar(50), year integer, mileage varchar(30), fuel varchar(30), transm varchar(30), body_type varchar(50), drive varchar(40), price varchar(20), link varchar(50))").format(
                sql.Identifier(make_id)))
            conn.commit()

        car_info['make'] = make_id
        get_user_model(message, make_id, car_info)




def get_user_model(message, make_id, car_info):

    models = main.get_model(make_id)
    bot.send_message(message.chat.id, "Выберите модель ", reply_markup=keyboard.model(models))
    bot.register_next_step_handler(message, get_user_model_input, car_info, models)

def get_user_model_input(message, car_info, models):
    selected_body_types = []
    body_types = main.get_body_type()

    model = message.text
    model_id = models[model]
    car_info['model'] = model_id

    bot.send_message(message.chat.id, "Выберите тип кузова", reply_markup=keyboard.body_type(body_types))
    bot.register_next_step_handler(message, get_user_body_type, selected_body_types, body_types, car_info)



def get_user_body_type(message, selected_body_types, body_types, car_info):
    body_type = message.text

    if body_type == "/stop":
        car_info['body_types'] = selected_body_types
        bot.send_message(message.chat.id, "Введите год начала")
        bot.register_next_step_handler(message, get_user_start_year, car_info)
    else:
        body_type_id = body_types[body_type]
        selected_body_types.append(body_type_id)

        bot.register_next_step_handler(message, get_user_body_type, selected_body_types, body_types, car_info)




def get_user_start_year(message, car_info):
    start_year = message.text
    if start_year == "пропустить":
        car_info['start_year'] = ""
    else:
        car_info['start_year'] = start_year

    bot.send_message(message.chat.id, "Введите год конца")
    bot.register_next_step_handler(message, get_user_end_year, car_info)


def get_user_end_year(message, car_info):
    fuels = main.get_fuel()
    end_year = message.text
    if end_year == "пропустить":
        car_info['end_year'] = ""
    else:
        car_info['end_year'] = end_year

    bot.send_message(message.chat.id, "выберите виды топлива", reply_markup=keyboard.fuel(fuels))
    selected_fuels = []
    bot.register_next_step_handler(message, get_user_fuel, fuels, car_info, selected_fuels)


def get_user_fuel(message, fuels, car_info, selected_fuels):
    selected_transms = []

    fuel = message.text

    transms = main.get_transm()

    if fuel == "/stop":
        car_info['fuels'] = selected_fuels
        bot.send_message(message.chat.id, "Выберите коробку передач", reply_markup=keyboard.transm(transms))
        bot.register_next_step_handler(message, get_user_transm, transms, car_info, selected_transms)
    else:
        fuel_id = fuels[fuel]
        selected_fuels.append(fuel_id)

        bot.register_next_step_handler(message, get_user_fuel, fuels, car_info, selected_fuels)


def get_user_transm(message, transms, car_info, selected_transms):
    selected_drivs = []

    transm = message.text
    drivs = main.get_driv()

    if transm == "/stop":
        car_info['transms'] = selected_transms
        bot.send_message(message.chat.id, "выберите привод", reply_markup=keyboard.driv(drivs))
        bot.register_next_step_handler(message, get_user_driv, drivs, car_info, selected_drivs)
    else:
        transm_id = transms[transm]
        selected_transms.append(transm_id)

        bot.register_next_step_handler(message, get_user_transm, transms, car_info, selected_transms)


def get_user_driv(message, drivs, car_info, selected_drivs):
    driv = message.text

    if driv == "/stop":
        car_info['drivs'] = selected_drivs

        construct_url(car_info, message)



        return searched_cars
    else:
        driv_id = drivs[driv]
        selected_drivs.append(driv_id)
        bot.register_next_step_handler(message, get_user_driv, drivs, car_info, selected_drivs)


def construct_url(car, message):
        global payload, base_url, model, make



        body_types = car['body_types']
        make = car['make']
        model = car['model']
        start_year = car['start_year']
        end_year = car['end_year']
        fuels = car['fuels']
        transms = car['transms']
        drivs = car['drivs']

        payload = {
            'j': body_types,
            'bn': '2',
            'a': '100',
            'b': make,
            'bw': model,
            'f1': start_year,
            'f2': end_year,
            'h': fuels,
            'i': transms,
            'p': drivs,
            'ae': '8',
            'af': '100'
        }

        base_url = "https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&b=2&b=" + str(make) + "&bw=" + str(model) + "&f1=" + str(start_year) + "&f2=" + str(end_year)

        fuel_url = ""
        transm_url = ""
        driv_url = ""
        body_type_url = ""

        for fuel in fuels:
            fuel_url += "&h%5B%5D=" + str(fuel)

        for transm in transms:
            transm_url += "&i%5B%5D=" + str(transm)

        for driv in drivs:
            driv_url += "&p%5B%5D=" + str(driv)

        for body_type in body_types:
            body_type_url += "&j%5B%5D=" + str(body_type)

        base_url += fuel_url + transm_url + driv_url + body_type_url + "&ae%5B%5D=" + "8" + "&af%5B%5D=" + "100"

        car['url'] = base_url
        car['payload'] = payload
        searched_cars.append(car)


        print("BASE URL: " + base_url)


        check_if_table_have_rows(payload, base_url, model, make)

        start_searching(message)

def start_searching(message):
    print(searched_cars)
    print("going in while true")
    while True:
        for car in searched_cars:
            res = main.request(car['payload'], car['url'], car['model'], car['make'], 4)
            if len(res) != 0:
                print("RESULT: " + str(res))
                bot.send_message(message.chat.id, str(res))
        print("60 sec start")
        time.sleep(60)
        print("60 sec over")



def check_if_table_have_rows(payload, base_url, model, make):
        cursor.execute(sql.SQL("SELECT ROW_NUMBER() OVER () as row_number FROM {}").format(sql.Identifier(make)))
            # Fetch the result
        row = cursor.fetchone()

        model_exists = sql.SQL("SELECT EXISTS(SELECT 1 FROM {} WHERE model_short = %s)").format(sql.Identifier(make))
        cursor.execute(model_exists, (str(model),))
        model_exists = cursor.fetchone()[0]



        if row is None:
            print("There is no rows in table " + make)
            main.request(payload, base_url, model, make, 1)

        elif row is not None and not model_exists:
            print("there is row but no such model")
            main.request(payload, base_url, model, make, 2)

        elif row and model_exists:
            print("there is row and model")
            main.request(payload, base_url, model, make, 3)





        # if all_variants == -1:
        #     bot.send_message(message.chat.id, "Машин не найдено")





#https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&aj=&ssid=103692755&j%5B%5D=3&b=4&bw=1189&f1=2003&f2=2010&h%5B%5D=2&i%5B%5D=2&p%5B%5D=2&p%5B%5D=3&ae=8&af=100&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA
#https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&b=2&b=4&bw=1189&f1=2003&f2=2010&h%5B%5D=2&i%5B%5D=2&p%5B%5D=2&p%5B%5D=3&j%5B%5D=7&ae%5B%5D=8&af%5B%5D=50




if  __name__ == '__main__':
    bot.polling(none_stop=True)