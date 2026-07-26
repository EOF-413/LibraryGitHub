import json
import urllib.error
import urllib.parse

from LH import Http
from LLS import log_init

log = log_init('modules/GitHub')

API_ROOT = 'https://api.github.com'


class GithubError(Exception):
    pass


class Github:
    """
    Общая библиотека поиска репозиториев, связанных с главным репозиторием.
    Связь определяется по ссылке на главный репозиторий в "О нас" - "Иконка настроек" - "Описание".

    Пример "О нас:
                    AmazingMultiTool - программа, созданная соединить все бот-программы в одно удобное приложение,
                    Наш основной репозиторий: https://github.com/EOF-413/AmazingMultiTool!"
    """

    @staticmethod
    def search(main_repo=None, per_page=100):
        """
        Возвращает словарь:
        {
            "NameOfRepo": {
                "DEV": ["DEV 1", "DEV 2", "DEV 3", "..."],
                "LINK": "https://github.com/owner/NameOfRepo",
                "FILES": {"EXE": "main.exe", "MAN": "manifest.json", "ICO": "icon.ico"},
                "RELEASE": "https://.../asset.zip"  # None, если релиза с zip-ассетом нет
            }
        }
        """

        if main_repo is None:
            raise GithubError('Не был передан основной репозиторий.')

        main_repo = main_repo.rstrip('/').replace('https://github.com/', '')

        query = urllib.parse.quote(f'"https://github.com/{main_repo}" in:description', safe='')

        try:
            data = Http.get_json(f'{API_ROOT}/search/repositories?q={query}&per_page={per_page}')
        except urllib.error.HTTPError as e:
            log.error(f"Не удалось найти репозитории, связанные с [{main_repo}]: {e}")
            raise GithubError(f'Не удалось загрузить список репозиториев: {e}')
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            log.error(f"Не удалось найти репозитории, связанные с [{main_repo}]: {e}")
            raise GithubError(f'Не удалось загрузить список репозиториев: {e}')

        items = data.get('items', [])
        count = data.get('total_count', len(items))
        if count > len(items):
            log.warning(f"Найдено {count} репозиториев, обработано {len(items)} (ограничение: {per_page}.).")

        dependents = {}
        for repo in items:
            owner = repo['owner']['login']
            name = repo['name']

            dependents[name] = {
                'DEV': [owner],
                'LINK': repo.get('html_url', f'https://github.com/{owner}/{name}'),
                'FILES': Github._scan(owner, name),
                'RELEASE': Github._latest(owner, name),
            }

        log.info(f"Найдено репозиториев, связанных с [{main_repo}]: {len(dependents)}.")
        return dependents

    @staticmethod
    def download(owner, repo, filename):
        """Скачивает файл из корня репозитория (ветка по умолчанию). None, если не удалось."""
        try:
            data = Http.get_json(f'{API_ROOT}/repos/{owner}/{repo}/contents/{filename}')
        except urllib.error.HTTPError as e:
            log.debug(f"Не удалось получить [{filename}] из {owner}/{repo}: {e}")
            return None
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            log.debug(f"Не удалось получить [{filename}] из {owner}/{repo}: {e}")
            return None

        download_url = data.get('download_url')

        if not download_url:
            return None

        try:
            return Http.get(download_url)
        except urllib.error.URLError as e:
            log.debug(f"Не удалось скачать [{filename}] из {owner}/{repo}: {e}")
            return None

    @staticmethod
    def _scan(owner, repo):
        try:
            items = Http.get_json(f'{API_ROOT}/repos/{owner}/{repo}/contents/')
        except urllib.error.HTTPError as e:
            log.debug(f"Не удалось получить список файлов {owner}/{repo}: {e}")
            return {}
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            log.debug(f"Не удалось получить список файлов {owner}/{repo}: {e}")
            return {}

        files = {}
        for item in items:
            if item.get('type') != 'file':
                continue
            name = item.get('name', '')
            lower = name.lower()
            if lower.endswith('.exe') and 'EXE' not in files:
                files['EXE'] = name
            elif lower == 'manifest.json':
                files['MAN'] = name
            elif lower == 'icon.ico':
                files['ICO'] = name
        return files

    @staticmethod
    def _latest(owner, repo):
        try:
            release = Http.get_json(f'{API_ROOT}/repos/{owner}/{repo}/releases/latest')
        except urllib.error.HTTPError as e:
            log.debug(f"Нет релизов у {owner}/{repo}: {e}")
            return None
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            log.debug(f"Не удалось получить релиз {owner}/{repo}: {e}")
            return None

        assets = release.get('assets', [])
        zip_assets = [a for a in assets if a.get('name', '').lower().endswith('.zip')]
        if not zip_assets:
            log.error(f"В последнем релизе {owner}/{repo} нет zip-ассета.")
            return None
        return zip_assets[0]['browser_download_url']
