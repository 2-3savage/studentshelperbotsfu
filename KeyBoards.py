from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Начало
greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add("Я студент").add("Я преподаватель")

# Добавил запланированные мероприятия для пользователя(По просьбе Никиты)
# Меню с админ-панелью
menu_admin_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Расписание").add("Админ-панель").add("Профиль") \
    .add("Рассылки") \
    .add("Посмотреть расписание группы").add("Запланированные мероприятия").add("Настройки") \
    .add("Поддержка разработчиков")

# Меню обычного пользователя
menu_user_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Расписание").add("Профиль").add("Рассылки") \
    .add("Посмотреть расписание другой группы").add("Запланированные мероприятия") \
    .add("Настройки").add("Поддержка разработчиков")

# Рассылки
mailing_lists_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Удалить рассылку").add("Меню")

# Профиль
profile_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Меню")

# Настройки
setting_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Рассылки").add('Запланированные мероприятия'). \
    add("Изменить информацию").add("Меню")

# Изменение информации о себе
change_information_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add("Изменить имя"). \
    add("Изменить группу").add("Назад")
change_information_kb2 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add("Поменять преподавателя") \
    .add("Назад")
# Рассылки, в которых состоит пользователь
mailing_lists_kb2 = ReplyKeyboardMarkup(resize_keyboard=True).add("Меню")

# Отправление рассылок из админ-панели
admin_panel = ReplyKeyboardMarkup(resize_keyboard=True).add("Отправить рассылку") \
    .add('Отправить рассылку всем пользователям').add("Меню")
admin_panel_teacher = ReplyKeyboardMarkup(resize_keyboard=True).add("Отправить рассылку") \
    .add("Меню")
# Запланированные мероприятия
events_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Добавить мероприятие").add("Удалить мероприятие").add("Меню")

# Универсальная кнопка(просто в меню)
universal_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Меню")

# Выбор дня недели
day_of_the_week_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Понедельник").add("Вторник") \
    .add("Среда").add("Четверг").add("Пятница").add("Суббота") \
    .add('Посмотреть расписание на след. неделю').add("Меню")
day_of_the_week_kb2 = ReplyKeyboardMarkup(resize_keyboard=True).add("Понедельник").add("Вторник") \
    .add("Среда").add("Четверг").add("Пятница").add("Суббота") \
    .add('Посмотреть расписание нынешней недели').add("Меню")
# Кнопки выбора института
institute_kb = ReplyKeyboardMarkup(resize_keyboard=True).add('ИКИТ').add('ВИИ').add('ГИ').add('ИСИ').add('ИАиД') \
    .add('ИГ').add('ИГДГиГ').add('ИИФиРЭ').add('ИМиФИ').add('ИНиГ').add('ИППС').add('ИТиСУ').add('ИУБП').add('ИФКСиТ') \
    .add('ИФиЯК').add('ИЦМиМ').add('ИЭиГ').add('ИЭГУиФ').add('ПИ').add('ЮИ').add('ИФБиБТ')

# Кнопки институтов
ikit_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("КИ20-17/1б (1 подгруппа)").add("КИ20-17/1б (2 подгруппа)")
gi_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("КИ20-02-5м")

# Поддержка разработчиков
developer_support_kb = ReplyKeyboardMarkup(resize_keyboard=True).add('Узнать команду разработчиков') \
    .add("Поддержать разработку телеграмм-бота").add("Меню")

developer_support_kb2 = ReplyKeyboardMarkup(resize_keyboard=True).add('Поддержать разработчиков 100 рублей') \
    .add("Поддержать разработчиков 250 рублей").add("Поддержать разработчиков 500 рублей") \
    .add("Поддержать разработчиков 1000 рублей").add('Поддержать разработчиков другой суммой').add('Меню')

# Локация и контакт
markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Отправить свой контакт ☎️', request_contact=True)
).add(
    KeyboardButton('Отправить свою локацию 🗺️', request_location=True)
)
return_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add("Меню")

yes_or_no_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add("Да").add("Изменить").add("Меню")
yes_or_no_keyboard2 = ReplyKeyboardMarkup(resize_keyboard=True).add("Да").add("Меню")
time_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("1 час").add('2 часа').add('3 часа').add('4 часа') \
    .add('5 часов').add("6 часов").add("12 часов").add('18 часов').add('24 часа').add('2 дня').add('3 дня') \
    .add('Неделя').add('Меню')
time_kb2 = ReplyKeyboardMarkup(resize_keyboard=True).add('Без таймера').add("1 час").add('2 часа').add('3 часа').add(
    '4 часа') \
    .add('5 часов').add("6 часов").add("12 часов").add('18 часов').add('24 часа').add('2 дня').add('3 дня') \
    .add('Неделя').add('Меню')
alphabet = {"а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у",
            "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я", 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
            'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4',
            '5', '6', '7', '8', '9', '0', '(', ')', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '.', ',', 'А', 'Б', 'В', 'Г', 'Д', 'Е',
            'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ',
            'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я', '-', '/', ' ', ''}
PRICE100 = types.LabeledPrice(label='Поддержка разработчиков 100 Рублей', amount=10000)
PRICE250 = types.LabeledPrice(label='Поддержка разработчиков 250 Рублей', amount=25000)
PRICE500 = types.LabeledPrice(label='Поддержка разработчиков 500 Рублей', amount=50000)
PRICE1000 = types.LabeledPrice(label='Поддержка разработчиков 1000 Рублей', amount=100000)