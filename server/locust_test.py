from locust import HttpUser, task, tag, between
import time
import random

# Статичные данные для тестирования
DATES_FROM = ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01']
DATES_TO = ['2023-09-01', '2023-10-01', '2023-11-01', '2023-12-01']
SKILLS = ['Python', 'SQL', 'Linux', 'Git']


class MyLocustUser(HttpUser):
    wait_time = between(1.0, 5.0)  # Добавляем немного задержки между задачами

    # Адрес, к которому клиенты (предположительно) обращаются в первую очередь (это может быть индексная страница, страница авторизации и т.п.)
    def on_start(self):
        self.client.get("/apidocs")    # базовый класс HttpUser имеет встроенный HTTP-клиент для выполнения запросов (self.client)

    @tag("get_vacancy_levels")
    @task(2)
    def get_vacancy_levels(self):
        from_id = random.randint(0, 3)
        to_id = random.randint(0, 3)
        date_from = DATES_FROM[from_id]
        date_to = DATES_TO[to_id]
        with self.client.get('/vacancy_levels', params={'date_from': date_from, 'date_to': date_to},
                             catch_response=True, name='/vacancy_levels') as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f'Status code is {response.status_code}')

    @tag("get_vacancies_by_key_skill")
    @task(2)
    def get_vacancies_by_key_skill(self):
        from_id = random.randint(0, 3)
        to_id = random.randint(0, 3)
        skill_id = random.randint(0, 3)
        date_from = DATES_FROM[from_id]
        date_to = DATES_TO[to_id]
        skill = SKILLS[skill_id]
        with self.client.get('/vacancies-by-skill',
                             params={'date_from': date_from, 'date_to': date_to, 'skills[]': skill},
                             catch_response=True, name='/vacancies-by-skill') as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f'Status code is {response.status_code}')
