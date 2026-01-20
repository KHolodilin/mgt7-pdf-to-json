# План работ по улучшению проекта

## Структура плана
Каждая задача включает:
1. Создание GitHub Issue
2. Создание ветки `feature/issue-{номер}-{название}`
3. Реализацию изменений
4. Тестирование и проверки
5. Коммит и push

---

## Issue #1: Улучшение покрытия тестами

### Ветка: `feature/issue-1-improve-test-coverage`

### Задачи:
- [ ] Добавить тесты для `cli.py` (сейчас 0% покрытия)
  - Тесты для всех CLI аргументов
  - Тесты для обработки ошибок в CLI
  - Тесты для exit codes
- [ ] Добавить тесты для `parser.py` (сейчас 9.55% покрытия)
  - Тесты для основных методов парсинга
  - Тесты для edge cases
  - Тесты для обработки различных форматов данных
- [ ] Добавить тесты для `artifacts.py` (сейчас 23.88% покрытия)
  - Тесты для создания артефактов
  - Тесты для очистки артефактов
  - Тесты для retention policy
- [ ] Добавить тесты для `date_utils.py` (сейчас 48.08% покрытия)
  - Тесты для всех форматов дат
  - Тесты для edge cases

### Цель покрытия: ≥85%

### По окончанию:
```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=85
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json
git add .
git commit -m "test: improve test coverage to 85%+"
```

---

## Issue #2: Улучшение обработки ошибок

### Ветка: `feature/issue-2-improve-error-handling`

### Задачи:
- [ ] Улучшить сообщения об ошибках в `extractor.py`
  - Более информативные сообщения при ошибках извлечения
  - Контекстная информация (номер страницы, тип ошибки)
- [ ] Улучшить сообщения об ошибках в `parser.py`
  - Указание конкретного поля, которое не удалось распарсить
  - Предложение возможных причин ошибки
- [ ] Улучшить сообщения об ошибках в `validator.py`
  - Детализация ошибок валидации
  - Указание пути к проблемному полю в JSON
- [ ] Добавить валидацию входных файлов до обработки
  - Проверка существования файла
  - Проверка формата файла (PDF)
  - Проверка размера файла
  - Проверка доступности файла для чтения

### По окончанию:
```bash
pytest
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json
python -m mgt7_pdf_to_json nonexistent.pdf  # Проверка обработки ошибок
git add .
git commit -m "feat: improve error handling and validation"
```

---

## Issue #3: Улучшение качества кода

### Ветка: `feature/issue-3-improve-code-quality`

### Задачи:
- [ ] Улучшить типизацию
  - Добавить type hints для всех публичных методов
  - Использовать `TypedDict` где уместно
  - Добавить `from __future__ import annotations` где нужно
- [ ] Добавить docstrings
  - Docstrings для всех публичных классов и методов
  - Использовать Google-style docstrings
  - Добавить примеры использования в docstrings
- [ ] Рефакторинг больших функций
  - Разбить большие функции в `parser.py` на более мелкие
  - Выделить общую логику в отдельные методы
  - Улучшить читаемость кода

### По окончанию:
```bash
mypy src/mgt7_pdf_to_json --ignore-missing-imports
pytest
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json
git add .
git commit -m "refactor: improve code quality and type hints"
```

---

## Issue #4: Добавление проверок безопасности в CI/CD

### Ветка: `feature/issue-4-add-security-checks`

### Задачи:
- [ ] Добавить `safety` для проверки уязвимостей зависимостей
  - Установить `safety` в dev dependencies
  - Добавить шаг в CI workflow
  - Настроить проверку при каждом PR
- [ ] Добавить `bandit` для статического анализа безопасности
  - Установить `bandit` в dev dependencies
  - Добавить шаг в CI workflow
  - Настроить конфигурацию bandit
  - Исключить ложные срабатывания
- [ ] Настроить Dependabot
  - Создать `.github/dependabot.yml`
  - Настроить автоматические обновления для:
    - Python dependencies
    - GitHub Actions
  - Настроить schedule (еженедельно)

### По окончанию:
```bash
safety check
bandit -r src/
pytest
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json
git add .
git commit -m "ci: add security checks (safety, bandit) and dependabot"
```

---

## Issue #5: Добавление статистики обработки

### Ветка: `feature/issue-5-add-processing-statistics`

### Задачи:
- [ ] Добавить сбор статистики в `pipeline.py`
  - Время начала обработки
  - Время окончания обработки
  - Количество страниц в PDF
  - Количество извлеченных таблиц
  - Количество распарсенных полей
- [ ] Добавить вывод статистики в JSON output
  - Новое поле `statistics` в метаданных
  - Включить статистику только при флаге `--include-stats`
- [ ] Добавить вывод статистики в логи
  - Логирование статистики на уровне INFO
  - Форматированный вывод в консоль
- [ ] Добавить CLI флаг `--include-stats`
  - Опциональный флаг для включения статистики
  - По умолчанию выключен

### По окончанию:
```bash
pytest
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json --include-stats
python -m mgt7_pdf_to_json examples/KA903UC002704392_mgt7a.pdf -o test_output2.json --include-stats
git add .
git commit -m "feat: add processing statistics (time, pages, tables)"
```

---

## Общий порядок выполнения

1. **Issue #1** - Улучшение покрытия тестами (базовая задача)
2. **Issue #2** - Улучшение обработки ошибок (важно для стабильности)
3. **Issue #3** - Улучшение качества кода (рефакторинг)
4. **Issue #4** - Добавление проверок безопасности (CI/CD)
5. **Issue #5** - Добавление статистики (новая функциональность)

---

## Шаблон для создания Issue в GitHub

```markdown
## Описание
[Описание задачи из плана]

## Задачи
- [ ] Задача 1
- [ ] Задача 2
- [ ] ...

## Критерии приемки
- [ ] Все тесты проходят
- [ ] Pre-commit проверки проходят
- [ ] Пробный запуск конвертации успешен
- [ ] Код закоммичен

## Ветка
`feature/issue-{номер}-{название}`
```

---

## Шаблон коммита

```
{type}({scope}): {subject}

{body}

Fixes #{issue_number}
```

Типы:
- `feat`: новая функциональность
- `fix`: исправление бага
- `test`: добавление/изменение тестов
- `refactor`: рефакторинг кода
- `ci`: изменения в CI/CD
- `docs`: изменения в документации
