import unittest
from datetime import datetime
from webapp import db
from webapp.models import Area, KeySkill, Vacancy, Employer
from webapp.service import insert_area, insert_keyskill, insert_vacancy, insert_employer, keyskill_vacancy
from sqlalchemy.orm import Session

class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        # Создаем тестовую базу данных
        db.create_all()

        # Создаем фикстуры
        self.area = insert_area(Area, 1, "Test Area")
        self.employer = insert_employer(Employer, 1, "Test Employer")
        self.created_at = datetime(2023, 11, 5).date()

    def tearDown(self):
        # Очищаем тестовую базу данных после каждого теста
        db.session.close()

    def test_insert_area(self):
        # Проверяем функцию insert_area
        self.assertIsInstance(self.area, Area)
        self.assertEqual(self.area.hh_id, 1)
        self.assertEqual(self.area.name, "Test Area")

    def test_insert_keyskill(self):
        # Проверяем функцию insert_keyskill
        skill = insert_keyskill(KeySkill, "Test Skill")
        self.assertIsInstance(skill, KeySkill)
        self.assertEqual(skill.name, "Test Skill")

    def test_insert_employer(self):
        # Проверяем функцию insert_employer
        self.assertIsInstance(self.employer, Employer)
        self.assertEqual(self.employer.hh_id, 1)
        self.assertEqual(self.employer.name, "Test Employer")

    def test_insert_vacancy(self):
        # Проверяем функцию insert_vacancy
        vacancy = insert_vacancy(
            Vacancy,
            hh_id=1,
            salary_from=30000,
            salary_to=50000,
            currency_id="USD",
            experience_id="1",
            schedule_id="full-time",
            employment_id="full",
            area_id=self.area.id,
            employer_id=self.employer.id,
            created_at=self.created_at,
            level="junior"
        )

        self.assertIsInstance(vacancy, Vacancy)
        self.assertEqual(vacancy.hh_id, 1)
        self.assertEqual(vacancy.salary_from, 30000)
        self.assertEqual(vacancy.salary_to, 50000)
        self.assertEqual(vacancy.currency_id, "USD")
        self.assertEqual(vacancy.experience_id, "1")
        self.assertEqual(vacancy.schedule_id, "full-time")
        self.assertEqual(vacancy.employment_id, "full")
        self.assertEqual(vacancy.area_id, self.area.id)
        self.assertEqual(vacancy.employer_id, self.employer.id)
        self.assertEqual(vacancy.created_at, self.created_at)
        self.assertEqual(vacancy.level, "junior")

    def test_keyskill_vacancy(self):
        # Подготавливаем данные для теста
        skills = ["Skill 1", "Skill 2", "Skill 3"]

        # Проверяем функцию keyskill_vacancy
        vacancy = insert_vacancy(
            Vacancy,
            hh_id=1,
            salary_from=30000,
            salary_to=50000,
            currency_id="USD",
            experience_id="1",
            schedule_id="full-time",
            employment_id="full",
            area_id=self.area.id,
            employer_id=self.employer.id,
            created_at=self.created_at,
            level="junior"
        )
        keyskill_vacancy(vacancy, skills)

        self.assertEqual(len(vacancy.keyskill), 3)  # Проверяем, что навыки добавлены к вакансии

if __name__ == '__main__':
    unittest.main()