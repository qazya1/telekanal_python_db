from database import *
from datetime import datetime
from table import draw_table

class AppInterface:
    def __init__(self):
        user = input("Введите имя пользователя: ")
        name = input("Введите названия базы данных: ")
        password = input("Введите пароль: ")
        self.database = DataBase(name, user, password)
        self.program_interface = ProgramInterface(self.database)
        self.translation_interface = TranslationInterface(self.database)
        self.ads_interface = AdsInterface(self.database)
        self.ourtranslation_interface = OurTranslationInterface(self.database)
        self.film_interface = FilmInterface(self.database)
        self.studio_interface = StudioInterface(self.database)
        self.show_interface = ShowInterface(self.database)
    
    def loop(self):
        while True:
            self.interface_req()
    
    def interface_req(self):
        print('''
        Выберите таблицу базы данных:
            Program - P
            ShowTable - ST
            Advertising - A
            Translation - T
            Film - F
            OurTranslation - OT
            Studio - S''')
        table_name_letter = input()
        if table_name_letter == 'P':
            self.program_interface.action_choice()
        elif table_name_letter == 'ST':
            self.show_interface.action_choice()
        elif table_name_letter == 'A':
            self.ads_interface.action_choice()
        elif table_name_letter == 'T':
            self.translation_interface.action_choice()
        elif table_name_letter == 'F':
            self.film_interface.action_choice()
        elif table_name_letter == 'OT':
            self.ourtranslation_interface.action_choice()
        elif table_name_letter == 'S':
            self.studio_interface.action_choice()

class TableInterface:
    def __init__(self, database):
        self.database = database

class ProgramInterface(TableInterface):
    def action_choice(self):
        print('''
        Выберите действие:
            Добавить программу - Доб
            Удалить программу - Удал
            Изменить программу - Изм
            Вывести список программ - Вывод''')
        action_letter = input()
        if action_letter == "Доб":
            self.create()
        elif action_letter == "Удал":
            self.delete()
        elif action_letter == "Изм":
            self.edit()
        elif action_letter == "Вывод":
            self.select()
    
    def input_params(self):
        day_or_date = input()
        values = day_or_date.split()
        days_list = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье")
        if len(values) == 1 and values[0] in days_list:
            return values[0], "day"
        elif len(values) == 3:
            try:
                year = int(values[0])
            except ValueError:
                return None
            month = values[1]
            day = values[2]
            try:
                if len(day) == 2 and day[0] == '0':
                    day_int = int(day[1:])
                else:
                    day_int = int(day)
            except ValueError:
                return None
            if 1980 <= year <= 2100 and month in ('01','02','03','04','05','06','07','08','09','10','11','12'):
                if (month in ('01','03','05','07','08','10','12') and 1 <= day_int <= 31) or (month in ('04','06','09','11') and 1 <= day_int <= 30) or (month == '02' and year%4!=0 and 1 <= day_int <= 28) or (month == '02' and year%4==0 and 1 <= day_int <= 29):
                    return f"{year}-{month}-{day}", "date"
        return None
    
    def create(self):
        print('''
        Выберите, когда будет идти программа:
            День недели - (день_недели)
        либо
            Определённая дата - (год) (месяц) (день)''')
        params = self.input_params()
        if params:
            self.database.program_table.create(*params)
        else:
            print("Ошибка ввода")

    def delete(self):
        print('''
        Выберите, когда идёт программа, которую нужно удалить:
            День недели - (день_недели)
        либо
            Определённая дата - (год) (месяц) (день)''')
        params = self.input_params()
        if params:
            self.database.program_table.delete(*params)
        else:
            print("Ошибка ввода")
    
    def edit(self):
        print('''
        Выберите, когда идёт программа, которую нужно изменить:
            День недели - (день_недели)
        либо
            Определённая дата - (год) (месяц) (день)''')
        params_old = self.input_params()
        if params_old:
            print('''
        Введите новый параметр:
            День недели - (день_недели)
        либо
            Определённая дата - (год) (месяц) (день)''')
            params_new = self.input_params()
            if params_new:
                self.database.program_table.edit(*params_old, *params_new)
        else:
            print("Ошибка ввода")
    
    def select(self):
        try:
            limit = int(input("Введите число строк, если хотите ограничить вывод: "))
        except ValueError:
            limit = None
        print("Информация обо всех программах:")
        rows_list = self.database.program_table.select(limit)
        draw_table(["dayName", "date"], rows_list)

class TranslationInterface(TableInterface):
    def action_choice(self):
        print('''
        Выберите действие:
            Добавить передачу - Доб
            Удалить передачу - Удал
            Изменить передачу - Изм
            Вывести список передач - Вывод''')
        action_letter = input()
        if action_letter == "Доб":
            self.create()
        elif action_letter == "Удал":
            self.delete()
        elif action_letter == "Изм":
            self.edit()
        elif action_letter == "Вывод":
            self.select()
    
    def create(self):
        name = input("Введите название передачи: ")
        self.database.translation_table.create(name)
    
    def delete(self):
        name = input("Введите название передачи: ")
        self.database.show_table.delete_by_translation(name)
        self.database.translation_table.delete(name)
    
    def edit(self):
        name_old = input("Введите название передачи, которую нужно изменить: ")
        name_new = input("Введите новое название передачи: ")
        self.database.translation_table.edit(name_old, name_new)
    
    def select(self):
        print("Информация выводится в алфавитном порядке")
        try:
            limit = int(input("Введите число строк, если хотите ограничить вывод: "))
        except ValueError:
            limit = None
        print("Информация обо всех программах:")
        rows_list = self.database.translation_table.select(limit)
        print("name")
        for i in rows_list:
            print(i)

class AdsInterface(TableInterface):
    def action_choice(self):
        print('''
        Выберите действие:
            Добавить рекламу - Доб
            Удалить рекламу - Удал
            Изменить рекламу - Изм
            Вывести список реклам - Вывод''')
        action_letter = input()
        if action_letter == "Доб":
            self.create()
        elif action_letter == "Удал":
            self.delete()
        elif action_letter == "Изм":
            self.edit()
        elif action_letter == "Вывод":
            self.select()
    
    def create(self):
        name = input("Введите название продукта: ")
        self.database.ads_table.create(name)
    
    def delete(self):
        name = input("Введите название продукта: ")
        self.database.show_table.delete_by_ads(name)
        self.database.ads_table.delete(name)
    
    def edit(self):
        name_old = input("Введите название продукта рекламы, которую нужно изменить: ")
        name_new = input("Введите новое название продукта: ")
        self.database.ads_table.edit(name_old, name_new)
    
    def select(self):
        print("Информация выводится в алфавитном порядке")
        try:
            limit = int(input("Введите число строк, если хотите ограничить вывод: "))
        except ValueError:
            limit = None
        print("Информация обо всех рекламах:")
        rows_list = self.database.ads_table.select(limit)
        print("productName")
        for i in rows_list:
            print(i)

class OurTranslationInterface(TableInterface):
    def action_choice(self):
        print('''
        Выберите действие:
            Добавить передачу - Доб
            Вывести список передач - Вывод''')
        action_letter = input()
        if action_letter == "Доб":
            self.create()
        elif action_letter == "Удал":
            self.delete()
        elif action_letter == "Изм":
            self.edit()
        elif action_letter == "Вывод":
            self.select()
    
    def create(self):
        name = input("Введите название передачи: ")
        address = input("Введите адрес студии: ")
        self.database.studio_table.create(address)
        self.database.ourtranslation_table.create(name, address)
    
    def delete(self):
        print('''
        Удалить передачу:
            по названию - имя (имя_передачи)
            по адресу студии - студия (адрес)
        ''')
        try:
            info = input().split()
            type_ = info[0]
            name_or_address = " ".join(info[1:])
        except ValueError:
            print("Некорректный ввод")
            return
        self.database.show_table.delete_by_ourtranslation(type_, name_or_address)
        self.database.ourtranslation_table.delete(type_, name_or_address)
    
    def edit(self):
        name_old = input("Введите название передачи, которую нужно изменить: ")
        name_new = input("Введите новое название передачи (Enter, чтобы оставить прежнее): ")
        address_new = input("Введите другой адрес студии (Enter, чтобы оставить прежний): ")
        if name_new == "":
            name_new = None
        if address_new == "":
            address_new = None
        self.database.ourtranslation_table.edit(name_old, name_new, address_new)
    
    def select(self):
        print('''
        Вывести передачи:
            фильтровать - ф
            вывести все в алфавитном порядке по названию - все
        ''')
        filter_flag = input()
        if filter_flag == "ф":
            print('''
            Фильтровать:
                по названию - имя (имя_передачи)
                по адресу студии - студия (адрес)
            ''')
            input_str = input().split()
            if input_str[0] == "студия":
                rows_list = self.database.ourtranslation_table.select(None, " ".join(input_str[1:]))
            elif input_str[0] == "имя":
                rows_list = self.database.ourtranslation_table.select(" ".join(input_str[1:]), None)
        elif filter_flag == "все":
            print("Информация выводится в алфавитном порядке")
            try:
                limit = int(input("Введите число строк, если хотите ограничить вывод: "))
            except ValueError:
                limit = None
            print("Информация обо всех программах:")
            rows_list = self.database.ourtranslation_table.select_all(limit)
        draw_table(["name", "addressStudio"], rows_list)

class FilmInterface(TableInterface):
    def action_choice(self):
        print('''
        Выберите действие:
            Добавить фильм - Доб
            Удалить фильм - Удал
            Изменить фильм - Изм
            Вывести список фильмов - Вывод''')
        action_letter = input()
        if action_letter == "Доб":
            self.create()
        elif action_letter == "Удал":
            self.delete()
        elif action_letter == "Изм":
            self.edit()
        elif action_letter == "Вывод":
            self.select()
    
    def create(self):
        name = input("Введите название фильма: ")
        serie = input("Введите серию (если нет серии, Enter): ")
        if serie == "":
            serie = None
        else:
            try:
                serie = int(serie)
            except ValueError:
                print("Ошибка ввода")
                return
        self.database.film_table.create(name, serie)
    
    def delete(self):
        name = input("Введите название фильма: ")
        serie = input("Введите серию (Enter, чтобы не указывать): ")
        if serie == "":
            serie = None
        self.database.show_table.delete_by_film(name, serie)
        self.database.film_table.delete(name)
    
    def edit(self):
        name_old = input("Введите название фильма, который нужно изменить: ")
        serie_old = input("Введите серию (Enter, чтобы не указывать): ")
        name_new = input("Введите новое название фильма(Enter, чтобы оставить прежним): ")
        serie_new = input("Введите серию (Enter, чтобы оставить прежним): ")
        if serie_old == "":
            serie_old = None
        if serie_new == "":
            serie_new = None
        self.database.film_table.edit(name_old, serie_old, name_new, serie_new)
    
    def select(self):
        print("Информация выводится в алфавитном порядке")
        try:
            limit = int(input("Введите число строк, если хотите ограничить вывод: "))
        except ValueError:
            limit = None
        print("Информация обо всех фильмах:")
        rows_list = self.database.film_table.select(limit)
        draw_table(["name", "serie_num"], rows_list)

class StudioInterface(TableInterface):
    def action_choice(self):
        print('''
        Выберите действие:
            Добавить студию - Доб
            Вывести список студий - Вывод''')
        action_letter = input()
        if action_letter == "Доб":
            self.create()
        elif action_letter == "Удал":
            self.delete()
        elif action_letter == "Изм":
            self.edit()
        elif action_letter == "Вывод":
            self.select()
    
    def create(self):
        address = input("Введите адрес студии: ")
        self.database.studio_table.create(address)
    
    def delete(self):
        address = input("Введите адрес студии: ")
        self.database.ourtranslation_table.delete("студия", address)
        self.database.studio_table.delete(address)
    
    def edit(self):
        address_old = input("Введите адрес студии, которую нужно изменить: ")
        address_new = input("Введите новый адрес студии: ")
        self.database.studio_table.edit(address_old, address_new)
    
    def select(self):
        print("Информация выводится в алфавитном порядке")
        try:
            limit = int(input("Введите число строк, если хотите ограничить вывод: "))
        except ValueError:
            limit = None
        print("Информация обо всех студиях:")
        rows_list = self.database.studio_table.select(limit)
        print("address")
        for i in rows_list:
            print(i)

class ShowInterface(TableInterface):
    def action_choice(self):
        print('''
        Выберите действие:
            Добавить показ - Доб
            Удалить показ - Удал
            Изменить показ - Изм
            Вывести список показов - Вывод''')
        action_letter = input()
        if action_letter == "Доб":
            self.create()
        elif action_letter == "Удал":
            self.delete()
        elif action_letter == "Изм":
            self.edit()
        elif action_letter == "Вывод":
            self.select()

    def input_params_program(self):
        day_or_date = input()
        values = day_or_date.split()
        days_list = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье")
        if len(values) == 1 and values[0] in days_list:
            return values[0], "day"
        elif len(values) == 3:
            try:
                year = int(values[0])
            except ValueError:
                return None
            month = values[1]
            day = values[2]
            try:
                if len(day) == 2 and day[0] == '0':
                    day_int = int(day[1:])
                else:
                    day_int = int(day)
            except ValueError:
                return None
            if 1980 <= year <= 2100 and month in ('01','02','03','04','05','06','07','08','09','10','11','12'):
                if (month in ('01','03','05','07','08','10','12') and 1 <= day_int <= 31) or (month in ('04','06','09','11') and 1 <= day_int <= 30) or (month == '02' and year%4!=0 and 1 <= day_int <= 28) or (month == '02' and year%4==0 and 1 <= day_int <= 29):
                    return f"{year}-{month}-{day}", "date"
        return None

    def check_time(self, hours, minutes):
        try:
            hours = int(hours)
        except ValueError:
            return False
        try:
            if len(minutes) == 2 and minutes[0] == '0':
                minutes = int(minutes[1:])
            else:
                minutes = int(minutes)
        except ValueError:
            return False
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return True
        return False
    
    def input_params_media(self, media_info, creating=False):
        if media_info[0] == "фильм":
            media_type = "film"
            name = media_info[1]
            if media_info[-2] == "серия":
                serie = media_info[-1]
                name = " ".join(media_info[1:-2])
            else:
                serie = None
                name = " ".join(media_info[1:])
            media_name = name+"@"+str(serie) if serie else name
            if creating:
                self.database.film_table.create(name, serie)
        elif media_info[0] == "передача" and len(media_info) >= 3 and media_info[1] == "наша":
            media_type = "ourtranslation"
            media_name = " ".join(media_info[2:])
            if creating:
                ot_id = self.database.show_table.get_ourtranslation_id(media_name)
                if not(ot_id):
                    print("Передачи не существует, добавим её")
                    address = input("Введите адрес студии, на которой снимается передача: ")
                    self.database.studio_table.create(address)
                    self.database.ourtranslation_table.create(media_name, address)
        elif media_info[0] == "передача" and len(media_info) >= 2:
            media_type = "translation"
            media_name = " ".join(media_info[1:])
            if creating:
                self.database.translation_table.create(media_name)
        elif media_info[0] == "реклама":
            media_type = "ads"
            media_name = " ".join(media_info[1:])
            if creating:
                self.database.ads_table.create(media_name)
        else:
            return None, None
        return media_type, media_name
    
    def create(self):
        print('''
        выберите программу, когда будет идти показ:
            день недели - (день_недели)
        либо
            определённая дата - (год) (месяц) (день)''')
        params_program = self.input_params_program()
        if not params_program:
            print("Ошибка ввода")
            return
        self.database.program_table.create(*params_program)
        print('''
        выберите, что будет идти в этот показ:
            фильм - фильм (название_фильма) (серия - необязательно)
        либо
            передача - передача (наша) (название_передачи)
        либо
            реклама - реклама (название_продукта)''')
        media_info = input().split()
        media_type, media_name = self.input_params_media(media_info, True)
        if not(media_type and media_name):
            print("Ошибка ввода")
            return
        print('''
        Выберите действие:
            Добавить показ вручную - Р
            Автоматически вставить показ в свободное место сетки вещания - А''')
        create_mode = input()
        if create_mode == "Р":
            time_start = input("Введите время начала показа в формате час:минута : ")
            if not(self.check_time(*time_start.split(":"))):
                print("Некорректный ввод")
                return
            time_finish = input("Введите время окончания показа в формате час:минута : ")
            if not(self.check_time(*time_finish.split(":"))):
                print("Некорректный ввод")
                return
            if datetime.strptime(time_start, "%H:%M") >= datetime.strptime(time_finish, "%H:%M"):
                print("Некорректный ввод: время начала позднее времени конца")
                return
            self.database.show_table.create(media_type, media_name, time_start, time_finish, *params_program)
        elif create_mode == "А":
            time_cont = input("Введите время продолжительности показа в формате час:минута : ")
            if not(self.check_time(*time_cont.split(":"))):
                print("Некорректный ввод")
                return
            self.database.show_table.create_find_time(media_type, media_name, time_cont, *params_program)
    
    def delete(self):
        print('''
        выберите программу, где надо удалить показы:
            день недели - (день_недели)
        либо
            определённая дата - (год) (месяц) (день)''')
        params_program = self.input_params_program()
        if not params_program:
            print("Ошибка ввода")
            return
        time_start = input("Введите время начала в формате час:минута : ")
        if not(self.check_time(*time_start.split(":"))):
            print("Некорректный ввод")
            return
        time_finish = input("Введите время окончания в формате час:минута : ")
        if not(self.check_time(*time_finish.split(":"))):
            print("Некорректный ввод")
            return
        print('''
        Выберите действие:
            Удалить показ с точным началом и концом - Т
            Удалить все показы в промежуток времени - П''')
        del_mode = input()
        if del_mode == "Т":
            self.database.show_table.delete(*params_program, time_start, time_finish)
        elif del_mode == "П":
            self.database.show_table.delete_in_interval(*params_program, time_start, time_finish)
    
    def edit(self):
        print('''
        выберите программу, где надо изменить показ:
            день недели - (день_недели)
        либо
            определённая дата - (год) (месяц) (день)''')
        params_program = self.input_params_program()
        if not params_program:
            print("Ошибка ввода")
            return
        print('''
        укажите, что идёт во время этих показов:
            фильм - фильм (название_фильма) (серия - необязательно)
        либо
            передача - передача (наша) (название_передачи)
        либо
            реклама - реклама (название_продукта)''')
        media_info = input().split()
        old_media_type, old_media_name = self.input_params_media(media_info)
        if not(old_media_type and old_media_name):
            print("Ошибка ввода")
            return
        print('''
        укажите, что должно идти во время этих показов:
            фильм - фильм (название_фильма) (серия - необязательно)
        либо
            передача - передача (наша) (название_передачи)
        либо
            реклама - реклама (название_продукта)''')
        media_info = input().split()
        new_media_type, new_media_name = self.input_params_media(media_info, True)
        if not(new_media_type and new_media_name):
            print("Ошибка ввода")
            return
        self.database.show_table.update(*params_program, old_media_type, old_media_name, new_media_type, new_media_name)
    
    def select(self):
        print('''
        выберите программу, показы которой выводим:
            день недели - (день_недели)
        либо
            определённая дата - (год) (месяц) (день)''')
        params_program = self.input_params_program()
        if not params_program:
            print("Ошибка ввода")
            return
        print('''
        Выберите действие:
            Фильтруем по медиа - М
            Фильтруем по временному промежутку - В
            Показываем всё - все''')
        filter_mode = input()
        if filter_mode == "М":
            print('''
            укажите, что идёт во время этих показов:
                фильм - фильм (название_фильма) (серия - необязательно)
            либо
                передача - передача (наша) (название_передачи)
            либо
                реклама - реклама (название_продукта)''')
            media_info = input().split()
            media_type, media_name = self.input_params_media(media_info)
            if not(media_type and media_name):
                print("Ошибка ввода")
                return
            rows_list = self.database.show_table.select_by_media(*params_program, media_type, media_name)
        elif filter_mode == "В":
            time_start = input("Введите время начала в формате час:минута : ")
            if not(self.check_time(*time_start.split(":"))):
                print("Некорректный ввод")
                return
            time_finish = input("Введите время окончания в формате час:минута : ")
            if not(self.check_time(*time_finish.split(":"))):
                print("Некорректный ввод")
                return
            rows_list = self.database.show_table.select_by_time(*params_program, time_start, time_finish)
        else:
            try:
                limit = int(input("Введите число строк, если хотите ограничить вывод: "))
            except ValueError:
                limit = None
            print("Информация обо всех показах:")
            rows_list = self.database.show_table.select_all(*params_program, limit)
        draw_table(["timeStart", "timeFinish", "programDay", "programDate", "ourTranslation", "translation", "film", "serie", "advertising"], rows_list)