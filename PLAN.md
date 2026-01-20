# План работ по улучшению проекта

## Структура плана
Каждая задача включает:
1. Создание GitHub Issue
2. Создание ветки `feature/issue-{номер}-{название}`
3. **Переход на новую ветку** (вручную): `git checkout -b feature/issue-{номер}-{название}`
4. Реализацию изменений
5. Тестирование и проверки
6. Коммит изменений
7. **Push ветки** (вручную): `git push origin feature/issue-{номер}-{название}`
8. **Создание Pull Request** с веткой `main`/`master`

---

## Issue #1: Улучшение покрытия тестами

**Title (EN):** Improve test coverage to 85%+

**Description (EN):** Increase test coverage from current 73.14% to at least 85% by adding comprehensive tests for CLI, parser, artifacts, and date utilities modules. This will improve code reliability and maintainability.

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

**Title (EN):** Improve error handling and validation

**Description (EN):** Enhance error messages with more context and detailed information. Add input file validation before processing to provide better user experience and faster failure detection.

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
# Тестирование и проверки
pytest
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json
python -m mgt7_pdf_to_json nonexistent.pdf  # Проверка обработки ошибок

# Коммит
git add .
git commit -m "feat: improve error handling and validation

Fixes #2"

# Push и создание PR (вручную)
git push origin feature/issue-2-improve-error-handling
# Затем создать Pull Request через GitHub UI или CLI
```

---

## Issue #3: Улучшение качества кода

**Title (EN):** Improve code quality and type hints

**Description (EN):** Enhance code quality by adding comprehensive type hints, improving docstrings, and refactoring large functions. This will improve code readability, maintainability, and IDE support.

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
# Тестирование и проверки
mypy src/mgt7_pdf_to_json --ignore-missing-imports
pytest
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json

# Коммит
git add .
git commit -m "refactor: improve code quality and type hints

Fixes #3"

# Push и создание PR (вручную)
git push origin feature/issue-3-improve-code-quality
# Затем создать Pull Request через GitHub UI или CLI
```

---

## Issue #4: Добавление проверок безопасности в CI/CD

**Title (EN):** Add security checks to CI/CD pipeline

**Description (EN):** Integrate safety and bandit tools for dependency vulnerability scanning and static security analysis. Configure Dependabot for automatic dependency updates to keep the project secure and up-to-date.

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
# Тестирование и проверки
safety check
bandit -r src/
pytest
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json

# Коммит
git add .
git commit -m "ci: add security checks (safety, bandit) and dependabot

Fixes #4"

# Push и создание PR (вручную)
git push origin feature/issue-4-add-security-checks
# Затем создать Pull Request через GitHub UI или CLI
```

---

## Issue #5: Добавление статистики обработки

**Title (EN):** Add processing statistics feature

**Description (EN):** Implement processing statistics collection and reporting including processing time, number of pages, extracted tables, and parsed fields. Add optional CLI flag to include statistics in output JSON and logs.

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
# Тестирование и проверки
pytest
pre-commit run --all-files
python -m mgt7_pdf_to_json examples/U17120DL2013PTC262515_mgt7.pdf -o test_output.json --include-stats
python -m mgt7_pdf_to_json examples/KA903UC002704392_mgt7a.pdf -o test_output2.json --include-stats

# Коммит
git add .
git commit -m "feat: add processing statistics (time, pages, tables)

Fixes #5"

# Push и создание PR (вручную)
git push origin feature/issue-5-add-processing-statistics
# Затем создать Pull Request через GitHub UI или CLI
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

**Важно:** Все описание issue должно быть полностью на английском языке.

```markdown
## Description
[English description from plan]

## Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] ...

## Acceptance Criteria
- [ ] All tests pass
- [ ] Pre-commit checks pass
- [ ] Test conversion run successful
- [ ] Code committed
- [ ] Branch pushed to remote repository
- [ ] Pull Request created with main branch
```

**Примечание:** Раздел "Branch" не нужно включать в описание issue. Ветка создается автоматически по шаблону `feature/issue-{номер}-{название}`.

## Шаги выполнения

1. **Создать и перейти на ветку** (вручную):
   ```bash
   git checkout -b feature/issue-{номер}-{название}
   ```

2. Выполнить задачи из списка выше

3. После завершения работы:
   ```bash
   # Тестирование
   pytest
   pre-commit run --all-files
   python -m mgt7_pdf_to_json examples/... -o test_output.json

   # Коммит
   git add .
   git commit -m "{type}: {description}

   Fixes #{номер}"

   # Push (вручную)
   git push origin feature/issue-{номер}-{название}
   ```

4. **Создать Pull Request** через GitHub UI или CLI (вручную)

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
