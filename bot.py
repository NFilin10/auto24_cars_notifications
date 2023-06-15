import telebot
from token import token
import keyboard
import main

bot = telebot.TeleBot(token)

searched_cars = []

selected_makes = []
selected_makes_ids = []
interested_models = {}
start_end_years = []
# selected_fuels = []
# selected_transms = []
# selected_drivs = []

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
    model = message.text
    model_id = models[model]
    car_info['model'] = model_id
    bot.send_message(message.chat.id, "Введите год начала")
    bot.register_next_step_handler(message, get_user_start_year, car_info)

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
    else:
        driv_id = drivs[driv]
        selected_drivs.append(driv_id)
        bot.register_next_step_handler(message, get_user_driv, drivs, car_info, selected_drivs)






if  __name__ == '__main__':
    bot.polling(none_stop=True)