from telebot import types


def make(makes):
    makes_list = []
    makes_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for make in makes.keys():
        button_make = types.KeyboardButton(make)
        makes_list = makes_markup.add(button_make)
    return makes_list


def model(models):
    models_list = []
    models_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for model in models.keys():
        button_make = types.KeyboardButton(model)
        models_list = models_markup.add(button_make)
    return models_list


def fuel(fuels):
    fuels_list = []
    fuels_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for fuel in fuels.keys():
        button_fuel = types.KeyboardButton(fuel)
        fuels_list= fuels_markup.add(button_fuel)
    return fuels_list


def transm(transms):
    transms_list = []
    transms_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for transm in transms.keys():
        button_transm = types.KeyboardButton(transm)
        transms_list = transms_markup.add(button_transm)
    return transms_list


def driv(drivs):
    drivs_list = []
    drivs_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for driv in drivs.keys():
        button_driv = types.KeyboardButton(driv)
        drivs_list = drivs_markup.add(button_driv)
    return drivs_list
