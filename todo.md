добавить подключение к postgres (asyncpg)
добавить хеширование паролей
~~разделить по файлам~~
почитать - https://fastapi.tiangolo.com/advanced/events/
почитать статью по алхимии

тз 2



fastapi best practice - в том числе разделение файлов  

posts
│   │   ├── router.py  - end points
│   │   ├── schemas.py - pydantic
│   │   ├── models.py  - sqlalchemy
│   │   ├── dependencies.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py