import telebot
from cfg import bot_token, cursor
import keyboard
import main


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
        print("Selected transms: ", selected_transms)
        bot.send_message(message.chat.id, "выберите привод", reply_markup=keyboard.driv(drivs))
        bot.register_next_step_handler(message, get_user_driv, drivs, car_info, selected_drivs)
    else:
        transm_id = transms[transm]
        selected_transms.append(transm_id)

        bot.register_next_step_handler(message, get_user_transm, transms, car_info, selected_transms)


def get_user_driv(message, drivs, car_info, selected_drivs):
    driv = message.text

    if driv == "/stop":
        print("Selected drivs: ", selected_drivs)
        car_info['drivs'] = selected_drivs
        searched_cars.append(car_info)
        # selected_drivs.clear()
        # selected_fuels.clear()
        # selected_transms.clear()
        print(searched_cars)
        construct_url(message, searched_cars)
        return searched_cars
    else:
        driv_id = drivs[driv]
        selected_drivs.append(driv_id)
        bot.register_next_step_handler(message, get_user_driv, drivs, car_info, selected_drivs)


def construct_url(message, searched_cars):
    car = searched_cars[len(searched_cars) - 1]
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
        'af': '50'
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

    base_url += fuel_url + transm_url + driv_url + body_type_url + "&ae%5B%5D=" + "8" + "&af%5B%5D=" + "50"
    print(base_url)
    all_variants = main.all_variants(payload, base_url, model)
    if all_variants == -1:
        bot.send_message(message.chat.id, "Машин не найдено")

    # else:
    #     fill_db()



#https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&aj=&ssid=103692755&j%5B%5D=3&b=4&bw=1189&f1=2003&f2=2010&h%5B%5D=2&i%5B%5D=2&p%5B%5D=2&p%5B%5D=3&ae=8&af=100&otsi=%D0%BF%D0%BE%D0%B8%D1%81%D0%BA
#https://rus.auto24.ee/kasutatud/nimekiri.php?bn=2&a=100&b=2&b=4&bw=1189&f1=2003&f2=2010&h%5B%5D=2&i%5B%5D=2&p%5B%5D=2&p%5B%5D=3&j%5B%5D=7&ae%5B%5D=8&af%5B%5D=50




if  __name__ == '__main__':
    bot.polling(none_stop=True)