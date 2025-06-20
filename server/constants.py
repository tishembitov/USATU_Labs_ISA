from enum import Enum


class Levels(Enum):
    UNDEFINED = []
    SENIOR = ["senior", "сеньор", "сеньёр", "синьёр", "сениор", "сеньер", "старший"]
    MIDDLE = ["middle", "миддл", "мидл"]
    JUNIOR = ["junior", "джуниор", "младший"]


labels = ('Junior', 'Middle', 'Senior')

SLEEP_TIME = 0.3

search_text = [
    'python junior',
    'python middle',
    'python senior',
    'python lead',
    'python backend',
    'python back-end',
    'python engineer',
    'python инженер',
    'python team lead',
    'python developer',
    'разработчик python',
    'программист python',
    'python-разработчик',
    'python разработчик',
    'python-программист',
    'python программист',
    'qa automation python',
    'Senior QA Automation Engineer Python',
    'Python Django developer'
    ]

experience = [
    {"id": "noExperience", "name": "Нет опыта"},
    {"id": "between1And3", "name": "От 1 года до 3 лет"},
    {"id": "between3And6", "name": "От 3 до 6 лет"},
    {"id": "moreThan6", "name": "Более 6 лет"}
]

employment = [
    {"id": "full", "name": "Полная занятость"},
    {"id": "part", "name": "Частичная занятость"},
    {"id": "project", "name": "Проектная работа"},
    {"id": "volunteer", "name": "Волонтерство"},
    {"id": "probation", "name": "Стажировка"}
]

schedule = [
    {"id": "fullDay", "name": "Полный день"},
    {"id": "shift", "name": "Сменный график"},
    {"id": "flexible", "name": "Гибкий график"},
    {"id": "remote", "name": "Удаленная работа"},
    {"id": "flyInFlyOut", "3name": "Вахтовый метод"}
]

currency = [
    {"code": "AZN", "name": "Манаты"},
    {"code": "BYR", "name": "Белорусские рубли"},
    {"code": "EUR", "name": "Евро"},
    {"code": "GEL", "name": "Грузинский лари"},
    {"code": "KGS", "name": "Киргизский сом"},
    {"code": "KZT", "name": "Тенге"},
    {"code": "RUR", "name": "Рубли"},
    {"code": "UAH", "name": "Гривны"},
    {"code": "USD", "name": "Доллары"},
    {"code": "UZS", "name": "Узбекский сум"}
]
