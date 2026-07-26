# LibraryGitHub (LGH)

**LGH** - это библиотека для работы с GitHub API. Позволяет искать репозитории, связанные с основным репозиторием, и скачивать файлы.

[Проект на PyPi!](https://pypi.org/project/EOF-413-LGH/1.0.0/)

## Особенности

- Поиск репозиториев, связанных с основным репозиторием (по ссылке в описании)
- Получение информации о файлах в корне репозитория
- Получение ссылки на последний релиз с ZIP-ассетом
- Интеграция с LibraryHttp (LH)
- Интеграция с LibraryLogSystem (LLS)

## Установка

```py
from LGH import Github
```

## Использование

### Поиск связанных репозиториев

# Поиск репозиториев, связанных с основным

```py
from LGH import Github

repos = Github.search('https://github.com/owner/main-repo')

# Поиск с ограничением количества
repos = Github.search('https://github.com/owner/main-repo', per_page=50)
```

### Скачивание файлов из репозитория

```py
from LGH import Github

# Скачивание файла из корня репозитория
file_content = Github.download('owner', 'repo', 'manifest.json')

if file_content:
    with open('manifest.json', 'wb') as f:
        f.write(file_content)
```

### Получение информации о файлах

```py
from LGH import Github

repos = Github.search('https://github.com/owner/main-repo')

for name, info in repos.items():
    print(f"Репозиторий: {name}")
    print(f"Разработчик: {info['DEV']}")
    print(f"Ссылка: {info['LINK']}")
    
    if info['FILES']:
        print("Файлы:")
        for key, value in info['FILES'].items():
            print(f"  {key}: {value}")
    
    if info['RELEASE']:
        print(f"Релиз: {info['RELEASE']}")
```

## API

### Github.search()

```py
Github.search(main_repo=None, per_page=100)
```

Ищет репозитории, связанные с основным репозиторием.

Параметры:

```PY
- main_repo (str): URL основного репозитория (по умолчанию: None)
- per_page (int): Количество результатов на страницу (по умолчанию: 100)
```

Возвращает:

```PY
- dict: Словарь с информацией о найденных репозиториях
```

Исключения:

```py
- GithubError: Ошибка при поиске или загрузке
```

### Github.download()

```py
Github.download(owner, repo, filename)
```

Скачивает файл из корня репозитория.

Параметры:

```py
- owner (str): Владелец репозитория
- repo (str): Название репозитория
- filename (str): Имя файла
```

Возвращает:

```py
- bytes: Содержимое файла или None если файл не найден
```

## Формат возвращаемых данных

```json
{
    "NameOfRepo": {
        "DEV": ["Developer 1", "Developer 2"],
        "LINK": "https://github.com/owner/NameOfRepo",
        "FILES": {
            "EXE": "main.exe",
            "MAN": "manifest.json",
            "ICO": "icon.ico"
        },
        "RELEASE": "https://github.com/owner/NameOfRepo/releases/download/v1.0/asset.zip"
    }
}
```

## Логирование

Все операции логируются через LLS в logs/GitHub/:

```log
[25.07.2026 21:59:18] [INFO] [repository.py] [search] [45] -> Найдено репозиториев, связанных с [owner/main-repo]: 5.
[25.07.2026 21:59:18] [ERROR] [repository.py] [search] [30] -> Не удалось найти репозитории: 404 Not Found
```

## Структура логов

```text
logs/
└── GitHub/
    ├── debug/
    ├── info/
    │   └── 21.59.18_25.07.2026.log
    ├── warnings/
    ├── errors/
    │   └── 21.59.18_25.07.2026.log
    └── critical/
```

## Зависимости

[LibraryHttp (LH)](https://github.com/EOF-413/LibraryHttp)
[LibraryLogSystem (LLS)](https://github.com/EOF-413/LibraryLogSystem)
