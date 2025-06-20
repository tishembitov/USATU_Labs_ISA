import logging
import requests
import time

from constants import Levels, SLEEP_TIME


logging.basicConfig(handlers=[logging.FileHandler('error.log', 'a', 'utf-8')],
                    format='%(levelname)s - %(message)s')


class HeadHunterClient:
    API_BASE_URL = 'https://api.hh.ru/'
    VACANCIES_LIST_PATH = 'vacancies/'
    AREAS_LIST_PATH = 'areas'

    def get_areas_ids(self) -> list:
        """
        Метод для получения списка id регионов.
        Используется для декомпозиции результатов поиска
        и обхода ограничений в 2000 вакансий
        """
        time.sleep(SLEEP_TIME)
        try:
            req = requests.get(f'{self.API_BASE_URL}{self.AREAS_LIST_PATH}')
            req.raise_for_status()
            answer = req.json()  # декодируем и приводим к питоновскому словарю
            if 'errors' in answer:
                raise ValueError('Запрос не выполнен')
        except ValueError as error:
            logging.exception(error)
            return
        except requests.RequestException as error:
            logging.exception(error)
            return
        areas_ids = [area['id'] for area in answer[0]['areas']]
        return areas_ids

    def get_vacancies_ids(self, vacancy_name, page, area=1) -> list:
        """Метод получения списка из id вакансий на странице.

        Возвращает список.
        Аргументы:
            vacancy_name - название требуемой вакансии
            page - номер страницы
            area - регион, по умолчанию = 1 (Москва)
        """
        params = {
            "area": area,
            "st": "searchVacancy",
            "text": vacancy_name,
            "page": page,
            "per_page": 100  # Параметр ограничен значением в 100 (из документации).
            }

        time.sleep(SLEEP_TIME)
        try:
            result = requests.get(f'{self.API_BASE_URL}{self.VACANCIES_LIST_PATH}', params=params)
            result.raise_for_status()
            vacancy_page = result.json()
            if 'errors' in vacancy_page:
                raise ValueError('Запрос не выполнен')
        except ValueError as error:
            logging.exception(error)
            return None, None
        except requests.RequestException as error:
            logging.exception(error)
            return None, None

        vacancy_ids = [vacancy["id"] for vacancy in vacancy_page["items"]]
        page_count = vacancy_page['pages']
        return vacancy_ids, page_count

    def get_vacancy_level(self, vacancy_page: dict) -> str:
        """ Метод получения уровня сосискателя (Junior, Middle, Senior) для вакансии

        Возвращает строку.
        Аргументы:
            vacancy_page - словарь с данными вакансии.
        """
        time.sleep(SLEEP_TIME)
        vacancy_sections = ["name", "description"]
        vacancy_level = Levels.UNDEFINED.name

        for section in vacancy_sections:
            for level in Levels:
                for similiar_level in level.value:
                    if similiar_level in vacancy_page[section].lower():
                        vacancy_level = level.name
        return vacancy_level

    def get_vacancy_detail(self, vacancy_id) -> dict:
        """
        Метод для получения нужной информации о вакансии.

        Аргументы:
            vacancy_id - id вакансии
        Возвращает словарь.
        """
        time.sleep(SLEEP_TIME)  # задержка для обхода ограничения 10 req/sec/ip
        # проверяем входные данные
        try:
            vacancy_id = int(vacancy_id)
        except TypeError as error:
            logging.exception(error)
            return
        except ValueError as error:
            logging.exception(error)
            return

        params = {
            'host': 'hh.ru'
        }

        # делаем запрос
        try:
            req = requests.get(f'{self.API_BASE_URL}{self.VACANCIES_LIST_PATH}{vacancy_id}', params)
            req.raise_for_status()
            answer = req.json()  # декодируем и приводим к питоновскому словарю
            if 'errors' in answer:
                raise ValueError('Запрос не выполнен')
        except ValueError as error:
            logging.exception(error)
            return
        except requests.RequestException as error:
            logging.exception(error)
            return

        vacancy_level = self.get_vacancy_level(answer)

        # формируем словарь
        data = {
            'hh_id': answer['id'],
            'name': answer['name'],
            'area_id': answer['area']['id'],
            'area_name': answer['area']['name'],
            'experience_id': answer['experience']['id'],
            'schedule_id': answer['schedule']['id'],
            'employment_id': answer['employment']['id'],
            'key_skills': answer['key_skills'],
            'created_at': answer['created_at'],
            'level': vacancy_level
        }

        """
        возможна ситуация, что у работодателя не указан id.
        За пишем для него id и name как None.
        """
        if 'id' in answer['employer']:
            data.update(
                {
                    'employer_id': answer['employer']['id'],
                    'employer_name': answer['employer']['name']
                }
            )
        else:
            data.update(
                {
                    'employer_id': None,
                    'employer_name': answer['employer']['name']
                }
            )

        # проверяем зарплату и дополняем словарь
        if answer['salary'] is None:
            data.update(
                {
                    'salary_from': None,
                    'salary_to': None,
                    'currency': None
                }
            )
        else:
            data.update(
                {
                    'salary_from': answer['salary']['to'],
                    'salary_to': answer['salary']['to'],
                    'currency': answer['salary']['currency']
                }
            )

        return data
