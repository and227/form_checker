## Требования:
- docker-compose, 1.29.2
- python, 3.7+

## Тестирование:

### Использование контейнера для тестов:
```bash
docker-compose --profile test up
```
Будет создан контейнер, добавляющий тестовые данны в базу и проверяющий запросы из файла tests/queries.txt

### Заполнение базы данных тестовыми формами из .json файла:
```bash
docker-compose --profile seed up
```
Запросы можно проверить через swagger:
```
http://localhost:8000/docs
```