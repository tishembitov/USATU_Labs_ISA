from datetime import date, datetime
from webapp import hh_app
from flask import render_template, request, flash
from flask import Flask, jsonify
from flasgger import Swagger
from sqlalchemy import func, desc
from webapp import db
from webapp.models import KeySkill, Vacancy, vacancy_skill
from webapp.dashboards import (create_pie_dashboard, create_salary_dashboard, create_salaries,
                               create_keyskills_dashboard, dash_link)
from constants import Levels

app = hh_app
Swagger(app)


@app.route('/vacancy_levels', methods=['GET'])
def vacancy_levels():
    """
    Get data on job vacancy levels.

    This endpoint returns data on job vacancy levels for a specified date range.

    ---
    parameters:
      - name: date_from
        in: query
        type: string
        format: date
        description: The start date for the data range.
      - name: date_to
        in: query
        type: string
        format: date
        description: The end date for the data range.
    responses:
      200:
        description: Data on job vacancy levels.
        schema:
          type: object
          properties:
            vacancy_levels:
              type: object
              description: Counts of job vacancies by level.
    """
    # Get query parameters
    get_date_from = request.args.get("date_from")
    get_date_to = request.args.get("date_to")

    # Convert date parameters
    date_from, date_to = get_date(get_date_from, get_date_to)

    # Fetch data based on the date range
    vacancy_levels = levels_counts(date_from, date_to)

    # Construct the response
    data = {
        'vacancy_levels': vacancy_levels,
    }

    return jsonify(data)

@app.route('/salary-of-levels', methods=['GET'])
def salary_of_levels():
    """
    Get salary of levels data.

    This endpoint returns the salary data based on job levels for a specified date range.

    ---
    responses:
      200:
        description: salary data based on job levels.
        schema:
          type: object
          description: salary information
    """
    # Fetch salary data based on levels and date range
    # Assuming create_salaries() function is utilized from the existing code
    junior_salaries = create_salaries(Levels.JUNIOR.name)
    middle_salaries = create_salaries(Levels.MIDDLE.name)
    senior_salaries = create_salaries(Levels.SENIOR.name)

    # Construct and return the response
    salary_data = {
        'junior': junior_salaries,
        'middle': middle_salaries,
        'senior': senior_salaries
    }
    return jsonify(salary_data)

@app.route('/vacancies-by-skill', methods=['GET'])
def vacancies_by_key_skill():
    """
    Get vacancies by key skill.

    This endpoint returns the number of vacancies based on specific key skills for a specified date range.

    ---
    parameters:
      - name: date_from
        in: query
        type: string
        format: date
        description: The start date for the data range.
      - name: date_to
        in: query
        type: string
        format: date
        description: The end date for the data range.
      - name: skills[]
        collectionFormat: multi
        in: query
        type: array
        items:
          type: string
        description: A list of specific key skills to filter the data.
    responses:
      200:
        description: Number of vacancies based on specific key skills.
        schema:
          type: object
          description: Vacancy counts by key skill
    """
    # Get query parameters
    get_date_from = request.args.get("date_from")
    get_date_to = request.args.get("date_to")
    get_skills = request.args.getlist("skills[]")

    # Convert date parameters
    date_from, date_to = get_date(get_date_from, get_date_to)

    # Fetch vacancy counts by key skill
    key_skill_counts = keyskills_count(date_from, date_to, get_skills)

    return jsonify(key_skill_counts)

# The existing code where the Flask app is initialized and functions are defined


def levels_counts(date_from, date_to):
    """
    Функция делает запрос у БД с фильтрами по дате и уровню
    """
    levels_counts = db.session.query(
        Vacancy.level, func.count(Vacancy.level)
    ).group_by(
        Vacancy.level
    ).filter(
        Vacancy.created_at.between(date_from, date_to)
    ).all()
    counts = dict(levels_counts)
    return counts


def keyskills_count(date_from, date_to, keyskills: list):
    """
    Функция для подсчета навыков.
    Параметры:
        date_from - дата фильтрации от
        date_to - дата фильтрации до
        keyskills - список навыков которые интересуют. Если список не передается,
        то возвращается 20 самых частоупоминаемых навыков
    """
    query_base = db.session.query(
        KeySkill.name, func.count(vacancy_skill.c.keyskill_id).label('total')
    ).join(
        vacancy_skill
    ).join(
        Vacancy
    ).group_by(
        KeySkill.name
    ).filter(
        Vacancy.created_at.between(date_from, date_to)
    ).order_by(
        desc('total')
    )

    if keyskills:
        query_skills_counts = query_base.filter(
            KeySkill.name.in_(keyskills)
        )
    else:
        query_skills_counts = query_base.limit(20)

    skill_counts = dict(query_skills_counts.all())
    return skill_counts


def get_date(get_date_from, get_date_to):
    """
    Поскольку фильтация по дате присутствует на всех страницах,
    то вынес преобразование результата GET-запроса даты в отдельную функцию.

    Проверяем входящие данные (не пустые ли) и в зависимости от результата
    подставляем либо дефолтное значение, либо введеную дату.

    В случае если введенная дата начала позже даты окончания
    тоже подставляем дефолтные значения
    """
    if get_date_from == '' or get_date_from is None:
        date_from = datetime(2021, 1, 1).date()
    else:
        date_from = datetime.strptime(get_date_from, '%Y-%m-%d').date()

    if get_date_to == '' or get_date_to is None:
        date_to = date.today()
    else:
        date_to = datetime.strptime(get_date_to, '%Y-%m-%d').date()

    if date_from > date_to:
        date_from = datetime(2021, 1, 1).date()
        date_to = date.today()

    return date_from, date_to


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    page_text = "Привет!"
    return render_template("index.html", title="О проекте", page_text=page_text)


@app.route("/keyskills", methods=["GET"])
def keyskills():
    """
    Вывод столбчатой диаграммы по ключевым навыкам
    """
    get_date_from = request.args.get("date_from")
    get_date_to = request.args.get("date_to")
    get_skills = request.args.getlist("skills[]")

    date_from, date_to = get_date(get_date_from, get_date_to)  # проверка и преобразование дат
    raw_skills = db.session.query(KeySkill.name.distinct())  # получение списка всех скилов
    skills = [skill[0] for skill in raw_skills]

    image = dash_link(create_keyskills_dashboard(keyskills_count(date_from, date_to, get_skills)))

    date_to_str = date_to.strftime('%d.%m.%Y')
    date_from_str = date_from.strftime('%d.%m.%Y')
    if not get_date_from and not get_date_to:
        flash("Данные за все время:")
    elif not get_date_from:
        flash(f"Данные по {date_to_str}:")
    elif not get_date_to:
        flash(f"Данные с {date_from_str}:")
    else:
        flash(f"Данные с {date_from_str} по {date_to_str}:")

    return render_template(
        "keyskills.html",
        title="Ключевые навыки",
        image=image,
        skills=skills
    )


@app.route("/salary", methods=["GET"])
def salary():
    page_text = "Распределение зарплат"
    image = dash_link(create_salary_dashboard(
        create_salaries(Levels.JUNIOR.name),
        create_salaries(Levels.MIDDLE.name),
        create_salaries(Levels.SENIOR.name)))
    return render_template("salary.html", title="Распределение зарплат", page_text=page_text, image=image)


@app.route("/vacancies", methods=["GET"])
def vacancies():
    """
    Вывод круговой диаграммы со счетчиком вакансий по уровням
    """
    get_date_from = request.args.get("date_from")
    get_date_to = request.args.get("date_to")

    date_from, date_to = get_date(get_date_from, get_date_to)  # проверка и преобразование дат

    date_to_str = date_to.strftime('%d.%m.%Y')
    date_from_str = date_from.strftime('%d.%m.%Y')
    if not get_date_from and not get_date_to:
        flash("Данные за все время:")
    elif not get_date_from:
        flash(f"Данные по {date_to_str}:")
    elif not get_date_to:
        flash(f"Данные с {date_from_str}:")
    else:
        flash(f"Данные с {date_from_str} по {date_to_str}:")

    image = dash_link(create_pie_dashboard(levels_counts(date_from, date_to)))

    return render_template("vacancies.html", title="Количество вакансий по уровням", image=image)
