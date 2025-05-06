import mysql.connector as mysql_con
from datetime import datetime
from datetime import timedelta

class DataBase:
    def __init__(self, name, user, password):
        self.name = name
        self.user = user
        if password == "":
            self.cnx = mysql_con.connect(user=user, database=name)
        else:
            self.cnx = mysql_con.connect(user=user, database=name, passwd=password)
        self.show_table = ShowTable(self.cnx)
        self.studio_table = StudioTable(self.cnx)
        self.film_table = FilmTable(self.cnx)
        self.ourtranslation_table = OurTranslationTable(self.cnx)
        self.ads_table = AdsTable(self.cnx)
        self.translation_table = TranslationTable(self.cnx)
        self.program_table = ProgramTable(self.cnx)
    def __del__(self):
        self.cnx.close()

class AbstractTable:
    def __init__(self, cnx):
        self.cnx = cnx

    def time_to_str(self, dt):
        t1 = datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day, hour=0,minute=0)
        dt = t1+dt
        return dt.strftime('%H:%M')

class ShowTable(AbstractTable):
    def get_film_id(self, film_name, serie=None):
        cursor = self.cnx.cursor()
        if serie:
            query = f'''
                SELECT idFilm FROM film
                WHERE name = "{film_name}"
                AND serie_num = {serie}
            '''
        else:
            query = f'''
                SELECT idFilm FROM film
                WHERE name = "{film_name}"
            '''
        cursor.execute(query)
        filmId = None
        for i in cursor:
            filmId = i[0]
        cursor.close()
        return filmId

    def get_translation_id(self, translation_name):
        cursor = self.cnx.cursor()
        query = f'''
                SELECT idTranslation FROM translation
                WHERE name = "{translation_name}"
            '''
        cursor.execute(query)
        translationId = None
        for i in cursor:
            translationId = i[0]
        cursor.close()
        return translationId
    
    def get_ourtranslation_id(self, translation_name):
        cursor = self.cnx.cursor()
        query = f'''
                SELECT idOurTranslation FROM ourtranslation
                WHERE name = "{translation_name}"
            '''
        cursor.execute(query)
        translationId = None
        for i in cursor:
            translationId = i[0]
        cursor.close()
        return translationId

    def get_ads_id(self, ads_name):
        cursor = self.cnx.cursor()
        query = f'''
                SELECT idAdvertising FROM advertising
                WHERE productName = "{ads_name}"
            '''
        cursor.execute(query)
        idAdvertising = None
        for i in cursor:
            idAdvertising = i[0]
        cursor.close()
        return idAdvertising
        
    def get_program_id(self, program_info, program_type):
        cursor = self.cnx.cursor()
        if program_type == "date":
            query = f'''
                SELECT idProgram FROM program
                WHERE date = "{program_info}"
            '''
        elif program_type == "day":
            query = f'''
                SELECT idProgram FROM program
                WHERE dayName = "{program_info}"
            '''
        else:
            return None
        cursor.execute(query)
        idProgram = None
        for i in cursor:
            idProgram = i[0]
        cursor.close()
        return idProgram
        
    def create(self, media_type, media_name, time_start, time_finish, program_info, program_type):
        film_id = "NULL"
        translation_id = "NULL"
        ourTranslation_id = "NULL"
        advertising_id = "NULL"
        if media_type == "film":
            film_id = self.get_film_id(*media_name.split("@"))
        elif media_type == "translation":
            translation_id = self.get_translation_id(media_name)
        elif media_type == "ourtranslation":
            ourTranslation_id = self.get_ourtranslation_id(media_name)
        elif media_type == "ads":
            advertising_id = self.get_ads_id(media_name)
        program_id = self.get_program_id(program_info, program_type)
        cursor = self.cnx.cursor()
        query = f'''
            INSERT INTO ShowTable (timeStart, timeFinish, programId, ourTranslationId, translationId, filmId, advertisingId) VALUES
            ("{time_start}", "{time_finish}", {program_id}, {ourTranslation_id}, {translation_id}, {film_id}, {advertising_id});
        '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            if err.errno == 1062:
                print("Показ уже существует")
            else:
                print(f"Произошла ошибка: {err}")
        cursor.close()
    
    def create_find_time(self, media_type, media_name, time_cont, program_info, program_type):
        film_id = "NULL"
        translation_id = "NULL"
        ourTranslation_id = "NULL"
        advertising_id = "NULL"
        if media_type == "film":
            film_id = self.get_film_id(*media_name.split("@"))
        elif media_type == "translation":
            translation_id = self.get_translation_id(media_name)
        elif media_type == "ourtranslation":
            ourTranslation_id = self.get_ourtranslation_id(media_name)
        elif media_type == "ads":
            advertising_id = self.get_ads_id(media_name)
        program_id = self.get_program_id(program_info, program_type)
        cursor_read = self.cnx.cursor(buffered=True)
        query_read = f'''
            SELECT timeStart, timeFinish FROM ShowTable
            WHERE programId = {program_id}
            ORDER BY timeStart'''
        dHours, dMinutes = time_cont.split(":")
        dt = timedelta(hours=int(dHours), minutes=int(dMinutes))
        cursor_read.execute(query_read)
        last_timeFinish = timedelta(hours=0,minutes=0)
        for timeStart, timeFinish in cursor_read:
            if last_timeFinish+dt < timeStart:
                t1 = last_timeFinish
                t2 = last_timeFinish+dt
                print(f"Удалось найти место в интервале {self.time_to_str(t1)} - {self.time_to_str(t2)}")
                break
            last_timeFinish = timeFinish
        else:
            print("Не удалось найти место в сетке вещания")
            return
        cursor_read.close()
        cursor_write = self.cnx.cursor()
        query = f'''
            INSERT INTO ShowTable (timeStart, timeFinish, programId, ourTranslationId, translationId, filmId, advertisingId) VALUES
            ("{t1}", "{t2}", {program_id}, {ourTranslation_id}, {translation_id}, {film_id}, {advertising_id});
        '''
        try:
            cursor_write.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor_write.close()
    
    def delete(self, program_info, program_type, time_start, time_finish):
        cursor = self.cnx.cursor()
        program_id = self.get_program_id(program_info, program_type)
        if not(program_id):
            print("Такой программы нет")
            return
        query = f'''
            DELETE FROM ShowTable WHERE programId = {program_id} AND timeStart = "{time_start}" AND timeFinish = "{time_finish}"'''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()
        
    def delete_by_program(self, program_info, program_type):
        cursor = self.cnx.cursor()
        if program_type == "day":
            query = f'''
                DELETE FROM ShowTable WHERE
                programId = 
                (SELECT idProgram FROM program WHERE dayName = "{program_info}")
            '''
        else:
            query = f'''
                DELETE FROM ShowTable WHERE
                programId = 
                (SELECT idProgram FROM program WHERE date = "{program_info}")
            '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()
    
    def delete_by_ads(self, name):
        cursor = self.cnx.cursor()
        ad_id = self.get_ads_id(name)
        if not(ad_id):
            print("Такой рекламы нет")
            return
        query = f'''
            DELETE FROM ShowTable WHERE advertisingId = {ad_id}'''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()
    
    def delete_by_translation(self, name):
        cursor = self.cnx.cursor()
        tr_id = self.get_translation_id(name)
        if not(tr_id):
            print("Такой передачи нет")
            return
        query = f'''
            DELETE FROM ShowTable WHERE translationId = {tr_id}'''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()
    
    def delete_by_film(self, name, serie):
        cursor = self.cnx.cursor()
        film_id = self.get_film_id(name, serie)
        if not(film_id):
            print("Такого фильма нет")
            return
        query = f'''
            DELETE FROM ShowTable WHERE filmId = {film_id}'''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()
    
    def delete_by_ourtranslation(self, type_, name):
        cursor = self.cnx.cursor()
        if type_ == "имя":
            tr_id = self.get_ourtranslation_id(name)
            if not(tr_id):
                print("Такой передачи нет")
                return
            query = f'''
                DELETE FROM ShowTable WHERE ourTranslationId = {tr_id}'''
        elif type_ == "студия":
             query = f'''
                DELETE FROM ShowTable WHERE ourTranslationId IN
                    (SELECT idOurTranslation FROM ourtranslation WHERE studioId IN 
                        (SELECT idStudio FROM studio WHERE address = "{name}")
                        )'''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()
    
    def delete_in_interval(self, program_info, program_type, time_start, time_finish):
        cursor = self.cnx.cursor()
        program_id = self.get_program_id(program_info, program_type)
        if not(program_id):
            print("Такой программы нет")
            return
        query = f'''
            DELETE FROM ShowTable WHERE programId = {program_id}
            AND (timeStart BETWEEN "{time_start}" AND "{time_finish}"
            OR timeFinish BETWEEN "{time_start}" AND "{time_finish}"
            OR (timeStart <= "{time_start}" AND timeFinish >= "{time_finish}"))'''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()
    
    def update(self, program_info, program_type, old_media_type, old_media_name, new_media_type, new_media_name):
        old_film_id = "NULL"
        old_translation_id = "NULL"
        old_ourTranslation_id = "NULL"
        old_advertising_id = "NULL"
        program_id = self.get_program_id(program_info, program_type)
        if not(program_id):
            print("Такой программы нет")
            return
        if old_media_type == "film":
            old_film_id = self.get_film_id(*old_media_name.split("@"))
            if not(old_film_id):
                print("Такого фильма не существует!")
                return
            query1 = f'''
                WHERE
                programId = {program_id} AND
                filmId = {old_film_id}
                '''
        elif old_media_type == "translation":
            old_translation_id = self.get_translation_id(old_media_name)
            if not(old_translation_id):
                print("Такой передачи не существует!")
                return
            query1 = f'''
                WHERE
                programId = {program_id} AND
                translationId = {old_translation_id}
                '''
        elif old_media_type == "ourtranslation":
            old_ourTranslation_id = self.get_ourtranslation_id(old_media_name)
            if not(old_ourTranslation_id):
                print("Такой передачи не существует!")
                return
            query1 = f'''
                WHERE
                programId = {program_id} AND
                ourTranslationId = {old_ourTranslation_id}
                '''
        elif old_media_type == "ads":
            old_advertising_id = self.get_ads_id(old_media_name)
            if not(old_advertising_id):
                print("Такой рекламы не существует!")
                return
            query1 = f'''
                WHERE
                programId = {program_id} AND
                advertisingId = {old_advertising_id}
                '''
        new_film_id = "NULL"
        new_translation_id = "NULL"
        new_ourTranslation_id = "NULL"
        new_advertising_id = "NULL"
        if new_media_type == "film":
            new_film_id = self.get_film_id(*new_media_name.split("@"))
        elif new_media_type == "translation":
            new_translation_id = self.get_translation_id(new_media_name)
        elif new_media_type == "ourtranslation":
            new_ourTranslation_id = self.get_ourtranslation_id(new_media_name)
        elif new_media_type == "ads":
            new_advertising_id = self.get_ads_id(new_media_name)
        cursor = self.cnx.cursor()
        query = f'''
            UPDATE ShowTable
            SET ourTranslationId = {new_ourTranslation_id},
            translationId = {new_translation_id},
            filmId = {new_film_id},
            advertisingId = {new_advertising_id}
            ''' + query1
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()
    
    def select_by_media(self, program_info, program_type, media_type, media_name):
        cursor = self.cnx.cursor(buffered=True)
        if program_type == "date":
            if media_type == "film":
                film_data = media_name.split("@")
                if len(film_data) == 2:
                    name, serie = film_data
                    query = f'''
                        SELECT * FROM fullshowsinfo
                        WHERE
                        date = "{program_info}" AND
                        filmName = "{name}" AND
                        filmSerie = {serie}
                        '''
                else:
                    name = media_name
                    query = f'''
                        SELECT * FROM fullshowsinfo
                        WHERE
                        date = "{program_info}" AND
                        filmName = "{name}"
                        '''
            elif media_type == "translation":
                query = f'''
                    SELECT * FROM fullshowsinfo
                    WHERE
                    date = "{program_info}" AND
                    translationName = "{media_name}"
                    '''
            elif media_type == "ourtranslation":
                query = f'''
                    SELECT * FROM fullshowsinfo
                    WHERE
                    date = "{program_info}" AND
                    ourTranslationName = "{media_name}"
                    '''
            elif media_type == "ads":
                query = f'''
                    SELECT * FROM fullshowsinfo
                    WHERE
                    date = "{program_info}" AND
                    productName = "{media_name}"
                    '''
        elif program_type == "day":
            if media_type == "film":
                film_data = media_name.split("@")
                if len(film_data) == 2:
                    name, serie = film_data
                    query = f'''
                        SELECT * FROM fullshowsinfo
                        WHERE
                        dayName = "{program_info}" AND
                        filmName = "{name}" AND
                        filmSerie = {serie}
                        '''
                else:
                    name = media_name
                    print(name)
                    query = f'''
                        SELECT * FROM fullshowsinfo
                        WHERE
                        dayName = "{program_info}" AND
                        filmName = "{name}"
                        '''
            elif media_type == "translation":
                query = f'''
                    SELECT * FROM fullshowsinfo
                    WHERE
                    dayName = "{program_info}" AND
                    translationName = "{media_name}"
                    '''
            elif media_type == "ourtranslation":
                query = f'''
                    SELECT * FROM fullshowsinfo
                    WHERE
                    dayName = "{program_info}" AND
                    ourTranslationName = "{media_name}"
                    '''
            elif media_type == "ads":
                query = f'''
                    SELECT * FROM fullshowsinfo
                    WHERE
                    dayName = "{program_info}" AND
                    productName = "{media_name}"
                    '''
        cursor.execute(query)
        result_rows = []
        for i in cursor:
            result_rows.append(i)
        cursor.close()
        return result_rows
    
    def select_by_time(self, program_info, program_type, time_start, time_finish):
        cursor = self.cnx.cursor(buffered=True)
        if program_type == "date":
            query = f'''
                SELECT * FROM fullshowsinfo
                WHERE
                date = "{program_info}" AND (timeStart BETWEEN "{time_start}" AND "{time_finish}"
            OR timeFinish BETWEEN "{time_start}" AND "{time_finish}"
            OR (timeStart <= "{time_start}" AND timeFinish >= "{time_finish}"))'''
        elif program_type == "day":
            query = f'''
                SELECT * FROM fullshowsinfo
                WHERE
                dayName = "{program_info}" AND (timeStart BETWEEN "{time_start}" AND "{time_finish}"
            OR timeFinish BETWEEN "{time_start}" AND "{time_finish}"
            OR (timeStart <= "{time_start}" AND timeFinish >= "{time_finish}"))'''
        cursor.execute(query)
        result_rows = []
        for i in cursor:
            result_rows.append(i)
        cursor.close()
        return result_rows
    
    def select_all(self, program_info, program_type, limit):
        cursor = self.cnx.cursor(buffered=True)
        if program_type == "date":
            if limit:
                query = f'''
                        SELECT * FROM fullshowsinfo
                        WHERE
                        date = "{program_info}"
                        LIMIT {limit}
                        '''
            else:
                query = f'''
                        SELECT * FROM fullshowsinfo
                        WHERE
                        date = "{program_info}"
                        '''
        elif program_type == "day":
            if limit:
                query = f'''
                        SELECT * FROM fullshowsinfo
                        WHERE
                        dayName = "{program_info}"
                        LIMIT {limit}
                        '''
            else:
                query = f'''
                        SELECT * FROM fullshowsinfo
                        WHERE
                        dayName = "{program_info}"
                        '''
        cursor.execute(query)
        result_rows = []
        for i in cursor:
            result_rows.append(i)
        cursor.close()
        return result_rows

class StudioTable(AbstractTable):
    def create(self, address):
        cursor = self.cnx.cursor()
        query = f'''
            INSERT INTO Studio(address) VALUES
            ("{address}")
        '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            if err.errno == 1062:
                print("Студия уже существует")
            else:
                print(f"Произошла ошибка: {err}")
        cursor.close()

    def delete(self, address):
        cursor = self.cnx.cursor()
        query = f'''
                    DELETE FROM Studio WHERE
                    address = "{address}"
                '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()

    def edit(self, address_old, address_new):
        cursor_read = self.cnx.cursor(buffered=True)
        cursor = self.cnx.cursor()
        query = f'''
                            SELECT idStudio FROM Studio WHERE
                            address = "{address_old}"
                        '''
        cursor_read.execute(query)
        for i in cursor_read:
            idStudio = i[0]
        query = f'''
            UPDATE Studio
            SET address = "{address_new}"
            WHERE idStudio = {idStudio}
        '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
            return
        cursor_read.close()
        cursor.close()

    def select(self, limit):
        cursor = self.cnx.cursor(buffered=True)
        if limit:
            query = f'''SELECT address FROM Studio ORDER BY address LIMIT {limit}'''
        else:
            query = '''SELECT address FROM Studio ORDER BY address'''
        result_rows = []
        cursor.execute(query)
        for i in cursor:
            result_rows.append(i[0])
        cursor.close()
        return result_rows

class FilmTable(AbstractTable):
    def create(self, name, serie):
        cursor = self.cnx.cursor()
        if serie:
            query = f'''
                        INSERT INTO Film(name, serie_num) VALUES
                        ("{name}", {serie})
                    '''
        else:
            query = f'''
                        INSERT INTO Film(name) VALUES
                        ("{name}")
                    '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            if err.errno == 1062:
                print("Фильм уже существует")
            else:
                print(f"Произошла ошибка: {err}")
        cursor.close()

    def delete(self, name):
        cursor = self.cnx.cursor()
        query = f'''
                    DELETE FROM Film WHERE
                    name = "{name}"
                '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()

    def edit(self, name_old, serie_old, name_new, serie_new):
        cursor_read = self.cnx.cursor(buffered=True)
        cursor = self.cnx.cursor()
        if serie_old:
            query = f'''
                            SELECT idFilm FROM Film WHERE
                            name = "{name_old}" AND
                            serie_num = {serie_old}
                        '''
        else:
            query = f'''SELECT idFilm FROM Film WHERE
                            name = "{name_old}"
                            AND serie_num IS NULL
                        '''
        cursor_read.execute(query)
        for i in cursor_read:
            idFilm = i[0]
        if serie_new:
            query = f'''
                UPDATE Film
                SET name = "{name_new}",
                serie_num = {serie_new}
                WHERE idFilm = {idFilm}
            '''
        else:
            query = f'''
                UPDATE Film
                SET name = "{name_new}"
                WHERE idFilm = {idFilm}
            '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
            return
        cursor_read.close()
        cursor.close()

    def select(self, limit):
        cursor = self.cnx.cursor(buffered=True)
        if limit:
            query = f'''SELECT name, serie_num FROM Film ORDER BY name LIMIT {limit}'''
        else:
            query = '''SELECT name, serie_num FROM Film ORDER BY name'''
        result_rows = []
        cursor.execute(query)
        for name, serie in cursor:
            result_rows.append((name, serie))
        cursor.close()
        return result_rows

class OurTranslationTable(AbstractTable):
    def get_studio_id(self, address):
        cursor = self.cnx.cursor(buffered=True)
        query = f'''
                SELECT idStudio FROM Studio
                WHERE address = "{address}"
                '''
        cursor.execute(query)
        for i in cursor:
            idStudio = i[0]
        cursor.close()
        return idStudio

    def create(self, name, address):
        cursor = self.cnx.cursor()
        studioId = self.get_studio_id(address)
        query = f'''
            INSERT INTO OurTranslation(name, studioId) VALUES
            ("{name}", {studioId})
        '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            if err.errno == 1062:
                print("Передача уже существует")
            else:
                print(f"Произошла ошибка: {err}")
        cursor.close()

    def delete(self, type_, name_or_address):
        cursor = self.cnx.cursor()
        if type_ == "имя":
            query = f'''
                        DELETE FROM OurTranslation WHERE
                        name = "{name_or_address}"
                    '''
        elif type_ == "студия":
            studioId = self.get_studio_id(name_or_address)
            query = f'''
                        DELETE FROM OurTranslation WHERE
                        studioId = {studioId}
                    '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()

    def edit(self, name_old, name_new, address_new):
        cursor_read = self.cnx.cursor(buffered=True)
        cursor = self.cnx.cursor()
        query = f'''
                        SELECT idOurTranslation FROM OurTranslation WHERE
                        name = "{name_old}"
                        '''
        cursor_read.execute(query)
        for i in cursor_read:
            idOurTranslation = i[0]
        if address_new is None:
            query = f'''
                UPDATE OurTranslation
                SET name = "{name_new}"
                WHERE idOurTranslation = {idOurTranslation}
            '''
        elif name_new is None:
            studioId = self.get_studio_id(address_new)
            query = f'''
                UPDATE OurTranslation
                SET studioId = {studioId}
                WHERE idOurTranslation = {idOurTranslation}
            '''
        elif name_new is not None and address_new is not None:
            studioId = self.get_studio_id(address_new)
            query = f'''
                UPDATE OurTranslation
                SET studioId = {studioId},
                name = "{name_new}"
                WHERE idOurTranslation = {idOurTranslation}
            '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
            return
        cursor_read.close()
        cursor.close()

    def select_all(self, limit):
        cursor = self.cnx.cursor(buffered=True)
        if limit:
            query = f'''SELECT name, address FROM OurTranslation
                        INNER JOIN Studio
                        ON studioId = idStudio
                        ORDER BY name LIMIT {limit}'''
        else:
            query = '''SELECT name, address FROM OurTranslation
                        INNER JOIN Studio
                        ON studioId = idStudio
                        ORDER BY name'''
        result_rows = []
        cursor.execute(query)
        for i in cursor:
            result_rows.append((i[0], i[1]))
        cursor.close()
        return result_rows
    
    def select(self, name, address):
        cursor = self.cnx.cursor(buffered=True)
        if address is None:
            query = f'''SELECT name, address FROM OurTranslation
                        INNER JOIN Studio
                        ON studioId = idStudio
                        WHERE name = "{name}"'''
        elif name is None:
            query = f'''SELECT name, address FROM OurTranslation
                        INNER JOIN Studio
                        ON studioId = idStudio
                        WHERE address = "{address}"'''
        result_rows = []
        cursor.execute(query)
        for i in cursor:
            result_rows.append((i[0], i[1]))
        cursor.close()
        return result_rows

class AdsTable(AbstractTable):
    def create(self, name):
        cursor = self.cnx.cursor()
        query = f'''
            INSERT INTO Advertising(productName) VALUES
            ("{name}")
        '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            if err.errno == 1062:
                print("Реклама уже существует")
            else:
                print(f"Произошла ошибка: {err}")
        cursor.close()

    def delete(self, name):
        cursor = self.cnx.cursor()
        query = f'''
                    DELETE FROM Advertising WHERE
                    productName = "{name}"
                '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()

    def edit(self, name_old, name_new):
        cursor_read = self.cnx.cursor(buffered=True)
        cursor = self.cnx.cursor()
        query = f'''
                            SELECT idAdvertising FROM Advertising WHERE
                            productName = "{name_old}"
                        '''
        cursor_read.execute(query)
        for i in cursor_read:
            idAdvertising = i[0]
        query = f'''
            UPDATE Advertising
            SET productName = "{name_new}"
            WHERE idAdvertising = {idAdvertising}
        '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
            return
        cursor_read.close()
        cursor.close()

    def select(self, limit):
        cursor = self.cnx.cursor(buffered=True)
        if limit:
            query = f'''SELECT productName FROM Advertising ORDER BY productName LIMIT {limit}'''
        else:
            query = '''SELECT productName FROM Advertising ORDER BY productName'''
        result_rows = []
        cursor.execute(query)
        for i in cursor:
            result_rows.append(i[0])
        cursor.close()
        return result_rows

class TranslationTable(AbstractTable):
    def create(self, name):
        cursor = self.cnx.cursor()
        query = f'''
            INSERT INTO Translation(name) VALUES
            ("{name}")
        '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            if err.errno == 1062:
                print("Передача уже существует")
            else:
                print(f"Произошла ошибка: {err}")
        cursor.close()

    def delete(self, name):
        cursor = self.cnx.cursor()
        query = f'''
                    DELETE FROM Translation WHERE
                    name = "{name}"
                '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()

    def edit(self, name_old, name_new):
        cursor_read = self.cnx.cursor(buffered=True)
        cursor = self.cnx.cursor()
        query = f'''
                            SELECT idTranslation FROM Translation WHERE
                            name = "{name_old}"
                        '''
        cursor_read.execute(query)
        for i in cursor_read:
            idTranslation = i[0]
        query = f'''
            UPDATE Translation
            SET name = "{name_new}"
            WHERE idTranslation = {idTranslation}
        '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
            return
        cursor_read.close()
        cursor.close()

    def select(self, limit):
        cursor = self.cnx.cursor(buffered=True)
        if limit:
            query = f'''SELECT name FROM Translation ORDER BY name LIMIT {limit}'''
        else:
            query = '''SELECT name FROM Translation ORDER BY name'''
        result_rows = []
        cursor.execute(query)
        for i in cursor:
            result_rows.append(i[0])
        cursor.close()
        return result_rows

class ProgramTable(AbstractTable):
    def create(self, program_info, program_type):
        cursor = self.cnx.cursor()
        if program_type == "day":
            query = f'''
                INSERT INTO Program(dayName) VALUES
                ("{program_info}")
            '''
        else:
            query = f'''
                INSERT INTO Program(date) VALUES
                ("{program_info}")
            '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            if err.errno == 1062:
                print("Программа уже существует")
            else:
                print(f"Произошла ошибка: {err}")
        cursor.close()

    def delete(self, program_info, program_type):
        cursor = self.cnx.cursor()
        if program_type == "day":
            query = f'''
                DELETE FROM Program WHERE
                dayName = "{program_info}"
            '''
        else:
            query = f'''
                DELETE FROM Program WHERE
                date = "{program_info}"
            '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
        cursor.close()

    def edit(self, program_info_old, program_type_old, program_info_new, program_type_new):
        cursor_read = self.cnx.cursor(buffered=True)
        cursor = self.cnx.cursor()
        if program_type_old == "day":
            query = f'''
                SELECT idProgram FROM Program WHERE
                dayName = "{program_info_old}"
            '''
        else:
            query = f'''
                SELECT idProgram FROM Program WHERE
                date = "{program_info_old}"
            '''
        cursor_read.execute(query)
        for i in cursor_read:
            idProgram = i[0]
        if program_type_new == "day":
            query = f'''
                UPDATE Program
                SET dayName = "{program_info_new}"
                WHERE idProgram = {idProgram}
            '''
        else:
            query = f'''
                UPDATE Program
                SET date = "{program_info_new}"
                WHERE idProgram = {idProgram}
            '''
        try:
            cursor.execute(query)
            self.cnx.commit()
        except mysql_con.Error as err:
            print(f"Произошла ошибка: {err}")
            return
        cursor_read.close()
        cursor.close()

    def select(self, limit):
        cursor = self.cnx.cursor()
        if limit:
            query = f'''SELECT dayName, date FROM Program LIMIT {limit}'''
        else:
            query = '''SELECT dayName, date FROM Program'''
        result_rows = []
        cursor.execute(query)
        for i in cursor:
            result_rows.append((i[0] if i[0] else "", i[1] if i[1] else ""))
        cursor.close()
        return result_rows