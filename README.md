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
- GET /api/lessons/lessons/{id}/ - детали урока + прогресс пользователя по этому уроку
- POST /api/lessons/generate/ - генерация урока по проблемным зонам

Прогресс обучения
- GET /api/lessons/progress/ - лучшие показатели по урокам
- GET /api/lessons/progress/{id} - лучший показатель для одного урока
- Автоматическое обновление при сохранении TrainingSession

Статистика
- GET /api/stats/sessions/ - все тренировочные сессии
- GET /api/stats/sessions/{id}/ - детали одной сессии
- POST /api/stats/sessions/ - сохранить сессию тренировки (с обновлением прогресса, статистики букв и биграмм)
- DELETE /api/stats/sessions/{id}/ - удалить сессию
- GET /api/stats/dashboard/ - агрегированная краткая статистика пользователя
- GET /api/stats/daily/ - агрегированная дневная статистика за 30 дней
- GET /api/stats/letters/ - проблемные буквы
- GET /api/stats/bigrams/ - проблемные биграммы


-->



<!--
Back -> Lesson Retrieve -> Front
Front -> Stats (total & letters, bigrams agr) -> Back

POST /api/stats/sessions/
{
  "lesson": 1,
  "total_duration_seconds": 180,
  "total_characters_typed": 500,
  "total_errors": 15,
  "average_speed_wpm": 125,
  "accuracy_percentage": 96.5,
  "started_at": "2024-11-10T14:00:00Z",
  "finished_at": "2024-11-10T14:03:00Z",
  
  "letter_stats": [
    {"letter": "а", "occurrences": 15, "errors": 2, "average_hit_time_ms": 120},
    {"letter": "о", "occurrences": 8, "errors": 1, "average_hit_time_ms": 150}
  ],
  "bigram_stats": [
    {"bigram": "ао", "occurrences": 5, "errors": 1, "average_transition_time_ms": 130},
    {"bigram": "оа", "occurrences": 4, "errors": 0, "average_transition_time_ms": 110}
  ]
}
-->



<!--

TODO:
1) Decide what to do with this:
- GET /api/lessons/recommended/ - рекомендованные уроки

2) Now lessons are being generated using error rate. Consider speed?

NOT TESTED YET: added daily stats update (general, letters, bigrams) & created lesson generation -> sqlite doesn't support "overlap" in JSON fields :/ sad
-->
