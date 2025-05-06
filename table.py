from datetime import datetime, timedelta

def time_to_str(dt):
    t1 = datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day, hour=0,minute=0)
    dt = t1+dt
    return dt.strftime('%H:%M')

def draw_table(columns, data):
    # Проверка на пустые данные
    if not columns or not data:
        print("Нет данных для отображения")
        return
    
    # Проверка, что количество колонок соответствует данным
    for row in data:
        if len(row) != len(columns):
            print("Ошибка: количество элементов в строке не соответствует количеству колонок")
            return
    
    # Определяем ширину каждой колонки
    col_widths = []
    for i in range(len(columns)):
        max_width = len(str(columns[i]))
        if type(data[0][i]) == timedelta:
            if 5 > max_width:
                max_width = 5
        else:
            for row in data:
                cell_width = len(str(row[i]))
                if cell_width > max_width:
                    max_width = cell_width
        col_widths.append(max_width + 2)  # Добавляем немного padding
    # Функция для создания горизонтальной линии
    def create_horizontal_line():
        line = "+"
        for width in col_widths:
            line += "-" * width + "+"
        return line
    
    # Функция для создания строки с данными
    def create_row(row_data, is_header=False):
        row_str = "|"
        for i, item in enumerate(row_data):
            if type(item) == timedelta:
                cell = f"{time_to_str(item)}"
            else:
                if item != None:
                    cell = f"{str(item)}"
                else:
                    cell = ""
            # Выравниваем по левому краю с учетом ширины колонки
            cell = cell.ljust(col_widths[i]) + "|"
            row_str += cell
        return row_str
    
    # Рисуем таблицу
    horizontal_line = create_horizontal_line()
    
    print(horizontal_line)
    print(create_row(columns, is_header=True))
    print(horizontal_line)
    
    for row in data:
        print(create_row(row))
        print(horizontal_line)