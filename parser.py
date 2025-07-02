from pprint import pprint
from typing import Any, Dict
from bs4 import BeautifulSoup
from fastapi import HTTPException, UploadFile
import requests


def parse_suip_response(html_text: str) -> Dict[str, Any]:
    """парсит ответ от сервиса и возвращает json

    Args:
        html_text (str): html документ

    Returns:
        Dict[str, Any]: JSON объект с метаданными по файлу
    """
    soup = BeautifulSoup(html_text, "html.parser")
    main_div = soup.find("div", class_="news")
    pre_blocks = main_div.find("pre")
    text = pre_blocks.getText()
    preprocessed_text_list = text.split("\n")
    result = {}
    for item in preprocessed_text_list:

        if ":" not in item:
            tag = item
            result[tag] = {}
        else:
            key, value = item.split(": ")
            result[tag].update({key.strip(): value})

    return result


def upload_and_parse_file(file: UploadFile, url: str) -> Dict[str, str]:
    """Функция загрузки и обработки файла.

    Args:
        file (UploadFile): Файл для получения метаданных
        url (str): Ссылка на сервис обработки

    Raises:
        HTTPException: Ошибка доступа к внешнему сервису
        HTTPException: Ошибка парсинга данных

    Returns:
        Dict[str, str]: JSON объект с метаданными по файлу
    """
    contents = file.file.read()
    files = {"fileforsending": (file.filename, contents, file.content_type)}

    try:
        response = requests.post(url=url, files=files, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch from suip.biz: {str(e)}"
        )

    result = parse_suip_response(response.text)
    if not result:
        raise HTTPException(status_code=500, detail="Could not parse response")
    return result


def create_metadata_report():
    """Возвращает файл с отчетом по метадате документа"""
    pass
