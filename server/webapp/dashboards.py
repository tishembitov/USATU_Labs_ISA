from io import BytesIO
import base64

import matplotlib.pyplot as plt
import numpy as np
from pycbrf import ExchangeRates
from sqlalchemy import case, and_, not_, func

from webapp.models import Vacancy
from webapp import db
from constants import Levels, labels


def create_salaries(level: str):
    """
    Создает словарь с ключами в виде зарплат 
    и значениями в виде количества вакансий с такой зарплатой.

    Аргументы:
        level - уровень вакансии.
    """
    usd_rate = ExchangeRates()["USD"].rate
    eur_rate = ExchangeRates()["EUR"].rate
    salaries = {}
    # Создаем case содержащий ЗП для каждой вакансии, исключая вакансии без ЗП.
    total_salary = case(
    [
        (and_(Vacancy.salary_from != None, Vacancy.salary_to != None), (Vacancy.salary_from + Vacancy.salary_to) / 2),
        (Vacancy.salary_from == None, Vacancy.salary_to),
        (Vacancy.salary_to == None, Vacancy.salary_from),
        (Vacancy.salary_to == None, Vacancy.salary_from),
    ],
    ).label("total_salary")

    # Создаем case содержащий ЗП для каждой вакансии в RUR.
    total_salary_rur = case(
        [
            (Vacancy.currency_id == "USD", total_salary * usd_rate),
            (Vacancy.currency_id == "EUR", total_salary * eur_rate),
        ],
    ).label("total_salary_rur")

    # Делаем запрос в БД и получаем данные о ЗП вакансий и о количестве повторяющихся ЗП.
    vacancies = db.session.query(
        Vacancy, func.count("total_salary"), total_salary_rur, total_salary
    ).filter(
        Vacancy.level == level
    ).filter(
        not_(
            and_(
                Vacancy.salary_from == None, 
                Vacancy.salary_to == None
            )
        )
    ).group_by("total_salary").all()

    for vacancy in vacancies:
        _, salary_count, *_ = vacancy
        if vacancy.total_salary_rur is not None:
            salaries[vacancy.total_salary_rur] = salary_count
        else:
            salaries[vacancy.total_salary] = salary_count
    return salaries

def create_sorted_salaries(salaries: dict):
    """Создает список из количества вакансий по разным диапазонам зарплат."""
    number_of_ranges = 5
    sorted_salaries = [0 for i in range(number_of_ranges)]
    salary_step = 50000
    for salary in salaries.keys():
        salary_range = int(salary // salary_step)
        if salary_range >= number_of_ranges:
            salary_range = number_of_ranges - 1
        sorted_salaries[salary_range] += salaries[salary]
    return sorted_salaries

def dash_link(figure):
    """
    Создает ссылку на изображение для вставки в шаблон html.

    Аргументы:
        figure - объект фигуры.
    """
    # Save it to a temporary buffer.
    buf = BytesIO()
    figure.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f'data:image/png;base64,{data}'


def create_pie_dashboard(levels_count: dict):
    """
    Функция для построения круговой диаграммы
    Принимает словарь вида {'junior': count, 'middle': count, 'senior': count}
    """

    # добавил проверку ключей во входящем словаре и сравнением с контстантой labels
    # иначе если количество ключей не совпадает с labels то падает с ошибкой
    labels_name = [label for label in labels if label.upper() in levels_count]
    sizes = [levels_count[label.upper()] for label in labels_name]

    figure, ax = plt.subplots()
    ax.pie(
        sizes,
        labels=labels_name,
        autopct=lambda p: '{:.0f}'.format(p * sum(sizes) / 100),  # счетчик вместо процентов
        shadow=True,
        startangle=90
    )

    return figure


def create_keyskills_dashboard(keyskills_count: dict):
    """
    Функция для построения столбчатой диаграммы по навыкам
    Принимаетсловарь вида {'skill1': count, 'skill2': count}
    """
    names = list(keyskills_count.keys())
    values = [keyskills_count[name] for name in names]

    figure, ax = plt.subplots()
    ax.bar(names, values)
    ax.set_ylabel('Количество упоминаний')
    plt.subplots_adjust(bottom=0.3)  # увеличинени нижнего поля под графиком
    plt.xticks(rotation=30, ha='right', va='top', fontsize='small')  # наклон меток и размер шрифта

    return figure
    

def create_salary_dashboard(
    junior_salaries: dict,
    middle_salaries: dict,
    senior_salaries: dict):
    """
    Создает диаграмму зарплат по уровням.

    Аргументы:
        salary_dict - словарь с ключами в виде зарплат
        и значениями в виде количества вакансий с такой зарплатой.
    """
    junior_salary = create_sorted_salaries(junior_salaries)
    middle_salary = create_sorted_salaries(middle_salaries)
    senior_salary = create_sorted_salaries(senior_salaries)
        
    category_names = [
        "less than 50k",
        "50k - 100k",
        "100k - 150k",
        "150k - 200k",
        "200k and more"]
    results = {
        Levels.JUNIOR.name: junior_salary,
        Levels.MIDDLE.name: middle_salary,
        Levels.SENIOR.name: senior_salary
    }
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, data.shape[1]))
    # Размер горизонтальных колонок (ширина, высота).
    figure, ax = plt.subplots(figsize=(9, 5))
    ax.invert_yaxis()
    # Видимость шкалы по оси X.
    ax.xaxis.set_visible(True)
    # Значения шкалы по оси X.
    ax.set_xlim(-1, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                    label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, label_type='center', color=text_color)
    
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
            loc='lower left', fontsize='small')
    ax.set_xlabel("Количество вакансий")

    return figure
