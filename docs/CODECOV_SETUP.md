# План настройки публикации отчетов в Codecov

## Текущее состояние

В проекте уже настроена базовая интеграция с Codecov:
- ✅ В `.github/workflows/ci.yml` есть шаг загрузки coverage (строки 78-84)
- ✅ Генерируется `coverage.xml` файл
- ✅ Используется `codecov/codecov-action@v5`
- ✅ Badge добавлен в README.md

## Шаги для полной настройки

### 1. Регистрация в Codecov

1. Перейти на https://codecov.io
2. Войти через GitHub аккаунт
3. Добавить репозиторий `KHolodilin/mgt7-pdf-to-json`
4. Codecov автоматически создаст токен (не требуется для публичных репозиториев)

### 2. Создание конфигурационного файла Codecov

Создать файл `codecov.yml` в корне проекта:

```yaml
codecov:
  token: # Не требуется для публичных репозиториев
  bot: codecov[bot]
  ci:
    - github-actions

coverage:
  precision: 2
  round: down
  range: "70...100"
  
  status:
    project:
      default:
        target: 85%
        threshold: 1%
        base: auto
        branches:
          - main
          - master
    patch:
      default:
        target: 80%
        threshold: 1%
        base: auto

comment:
  layout: "reach, diff, flags, files, footer"
  behavior: default
  require_changes: false

flags:
  unittests:
    paths:
      - src/mgt7_pdf_to_json/
    carryforward: true

ignore:
  - "*/tests/*"
  - "*/test_*.py"
  - "*/__pycache__/*"
  - "*/__init__.py"
  - "*/__main__.py"
```

### 3. Обновление CI Workflow (опционально)

Текущая конфигурация уже корректна, но можно улучшить:

```yaml
- name: Upload coverage to Codecov
  if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.9'
  uses: codecov/codecov-action@v5
  with:
    file: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
    fail_ci_if_error: false  # Не падать если Codecov недоступен
    token: ${{ secrets.CODECOV_TOKEN }}  # Опционально для приватных репозиториев
    verbose: true  # Для отладки
```

### 4. Настройка в Codecov Dashboard

После первого успешного запуска CI:

1. Перейти в настройки репозитория на Codecov
2. Настроить:
   - **Coverage Threshold**: 85%
   - **Comment on Pull Requests**: Включено
   - **Status Checks**: Включено
   - **Badge**: Включено

### 5. Проверка работы

1. Создать тестовый PR
2. Дождаться завершения CI
3. Проверить:
   - Комментарий от Codecov в PR с отчетом
   - Badge в README обновляется
   - Статус проверки в PR (если включен)

## Текущая конфигурация в CI

```yaml
- name: Upload coverage to Codecov
  if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.9'
  uses: codecov/codecov-action@v5
  with:
    file: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
```

**Примечания:**
- Загрузка происходит только для Ubuntu + Python 3.9 (основная конфигурация)
- Используется файл `coverage.xml` который генерируется pytest-cov
- Флаг `unittests` для категоризации coverage

## Рекомендации

### Для публичных репозиториев (текущий случай)

- ✅ Токен не требуется
- ✅ Автоматическая интеграция с GitHub
- ✅ Бесплатный план достаточен

### Дополнительные возможности

1. **Комментарии в PR**: Автоматические комментарии с coverage diff
2. **Status Checks**: Проверка coverage как обязательный статус
3. **Coverage Reports**: Детальные отчеты на сайте Codecov
4. **История Coverage**: Графики изменения coverage во времени

## Troubleshooting

### Badge не обновляется

- Проверить, что репозиторий добавлен в Codecov
- Убедиться, что CI успешно загружает coverage
- Проверить правильность URL в badge

### Coverage не загружается

- Проверить наличие файла `coverage.xml`
- Убедиться, что шаг выполняется (`if` условие)
- Проверить логи CI на ошибки

### Coverage показывает 0%

- Проверить правильность путей в `--cov`
- Убедиться, что тесты запускаются
- Проверить конфигурацию `[tool.coverage.run]` в `pyproject.toml`

## Следующие шаги

1. ✅ Создать `codecov.yml` конфигурацию
2. ✅ Зарегистрировать репозиторий в Codecov
3. ✅ Обновить CI workflow (опционально)
4. ✅ Протестировать на тестовом PR
5. ✅ Настроить статус проверки (опционально)
