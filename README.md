## Веб-приложение для обучения слепому методу печати с адаптивной системой упражнений


<!--
## Технологии:
- Python
- React
- PostgreSQL

URLs:
- 

### Для пользователя:

Аутентификация
- POST /api/auth/users/ - регистрация
- POST /api/auth/jwt/create/ - получение токенов
- GET /api/auth/users/me/ - профиль

Уроки
- GET /api/lessons/lessons/ - список уроков (коротко) с прогрессом 
- GET /api/lessons/lessons/{id}/ - детали урока + прогресс
- POST /api/lessons/generate/ - генерация урока по проблемным зонам

Прогресс
- GET /api/lessons/progress/ - прогресс по урокам
- GET /api/lessons/progress/{id} - лучший показатель для одного урока
- Автоматическое обновление при сохранении TrainingSession

Статистика
- GET /api/stats/sessions/ - все сессии
- GET /api/stats/sessions/{id}/ - детали одной сессии
- POST /api/stats/sessions/ - сохранить сессию тренировки (с обновлением прогресса)
- DELETE /api/stats/sessions/{id}/ - удалить сессию


-->

<!--

--!-- Change ---!---

- GET /api/lessons/recommended/ - рекомендованные уроки


- GET /api/stats/dashboard/ - общая статистика
- GET /api/stats/letters/, /bigrams/ - детальная статистика
- GET /api/stats/problem-letters/, /problem-bigrams/ - проблемные зоны


-->