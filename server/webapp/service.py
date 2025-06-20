import sqlalchemy.orm.exc
import logging
from webapp import db
from webapp.models import KeySkill

logging.basicConfig(handlers=[logging.FileHandler('error.log', 'a', 'utf-8')],
                    format='%(levelname)s - %(message)s')


def get_or_create(model, **kwargs):
    """
    Делает запрос в БД, при наличии определенной записи,
    возвращает ее, при отсутствии, создаем и возвращаем.
    """
    try:
        model_object = model.query.filter_by(**kwargs).first()
    # Лишний аргумент в запросе.
    except sqlalchemy.exc.InvalidRequestError as error:
        logging.exception(error)
        return None, None
    if model_object:
        return model_object, False

    try:
        model_object = model(**kwargs)
        db.session.add(model_object)
        db.session.commit()
    # Один из аргументов Unique уже существует.
    except sqlalchemy.exc.IntegrityError as error:
        logging.exception(error)
        return None, None
    return model_object, True


def keyskill_vacancy(vacancy, keyskills):
    skills = [insert_keyskill(KeySkill, skill) for skill in keyskills]
    for skill in skills:
        vacancy.keyskill.append(skill)
        db.session.add(vacancy)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as error:
        logging.exception(error)
        return


def insert_area(model, area_id, area_name):
    """Записывает данные в таблицу Area."""
    model_object, model_exist = get_or_create(model, hh_id=area_id, name=area_name)
    return model_object


def insert_keyskill(model, key_skill):
    """Записывает данные в таблицу KeySkill."""
    model_object, model_exist = get_or_create(model, name=key_skill)
    return model_object


def insert_vacancy(
    model,
    hh_id,
    salary_from,
    salary_to,
    currency_id,
    experience_id,
    schedule_id,
    employment_id,
    area_id,
    employer_id,
    created_at,
    level
):
    """Записывает данные в таблицу Vacancy."""
    model_object, _ = get_or_create(
        model,
        hh_id=hh_id,
        salary_from=salary_from,
        salary_to=salary_to,
        currency_id=currency_id,
        experience_id=experience_id,
        schedule_id=schedule_id,
        employment_id=employment_id,
        area_id=area_id,
        employer_id=employer_id,
        created_at=created_at,
        level=level
    )
    return model_object


def insert_employer(model, hh_id, name):
    row, _ = get_or_create(model, hh_id=hh_id, name=name)
    return row
