from datetime import datetime

from webapp import hh_app
from webapp.models import Employer, Vacancy, Area
from webapp.service import insert_area, insert_vacancy, insert_employer, keyskill_vacancy
from api_client import HeadHunterClient
from constants import search_text


hh = HeadHunterClient()


def merge_vacancies_ids(text: str, area_id: int) -> list:
    """
    Функция для получения максимально возможного
    количества (2000) id вакансий на один запрос.

    """
    vacancies_ids_total = []
    for page in range(20):
        vacancies_ids_on_page, pages = hh.get_vacancies_ids(text, page, area_id)
        if vacancies_ids_on_page:
            vacancies_ids_total.extend(vacancies_ids_on_page)
        if (pages - page) <= 1:
            break
    return vacancies_ids_total


def write_to_db(vacancies_ids):
    with hh_app.app_context():
        for vacancy_id in vacancies_ids:
            """
            Что бы не дергать api по каждой вакансии при повторном запуске
            сначала проверим есть ли уже вакансия с hh_id в локальной базе.
            Если нет то будем запрашивать детали вакансии.
            """
            is_vacancy_add = Vacancy.query.filter_by(hh_id=vacancy_id).first()

            # если вакансия локальной БД переходим к следующей
            if is_vacancy_add:
                continue

            vacancy_detail = hh.get_vacancy_detail(vacancy_id)
            # проверяем получили ли мы данные, если да то пишем в БД
            if vacancy_detail:
                area = insert_area(Area, vacancy_detail['area_id'], vacancy_detail['area_name'])

                """
                Возможна ситуация что работодатель уже есть в базе но сменил имя
                Обрабатываем данную ситуацию
                """
                # пытаемся получить работодателя из базы
                employer = Employer.query.filter_by(hh_id=vacancy_detail['employer_id']).first()
                # если работника нет в базе, то пишем
                if employer is None:
                    employer = insert_employer(Employer, vacancy_detail['employer_id'], vacancy_detail['employer_name'])

                vacancy_obj = insert_vacancy(
                    Vacancy,
                    vacancy_detail['hh_id'],
                    vacancy_detail['salary_from'],
                    vacancy_detail['salary_to'],
                    vacancy_detail['currency'],
                    vacancy_detail['experience_id'],
                    vacancy_detail['schedule_id'],
                    vacancy_detail['employment_id'],
                    area.id,
                    employer.id,
                    datetime.strptime(vacancy_detail['created_at'], '%Y-%m-%dT%H:%M:%S%z').date(),
                    vacancy_detail['level']
                )

                keyskills = [skill['name'] for skill in vacancy_detail['key_skills']]
                keyskill_vacancy(vacancy_obj, keyskills)


def worker():
    areas_ids = hh.get_areas_ids()
    for text in search_text:
        for area_id in areas_ids:
            vacancies_id = merge_vacancies_ids(text, area_id)
            write_to_db(vacancies_id)


if __name__ == '__main__':
    worker()
