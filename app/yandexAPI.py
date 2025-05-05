# app/yandexAPI.py

import yadisk
from yadisk_async.exceptions import YaDiskError
from typing import Dict, Any, List, Union
from functools import wraps
from flask import jsonify

class APIRequestError(Exception):
    pass

def handle_yadisk_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except YaDiskError as e:
            raise APIRequestError(f"Ошибка Яндекс.Диска: {str(e)}")
    return wrapper


class YandexDiskAPI:
    def __init__(self, token: str):
        self.token = token
        self.client = yadisk.AsyncClient(token=self.token)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.client.close()

    @handle_yadisk_errors
    async def check_token(self) -> bool:
        return await self.client.check_token()

    @handle_yadisk_errors
    async def get_disk_info(self) -> Dict[str, Any]:
        disk_info = await self.client.get_disk_info()
        try:
            return disk_info.__dict__
        except Exception as e:
            raise APIRequestError(f"Не удалось получить информацию о диске: {str(e)}")

    @handle_yadisk_errors
    async def listdir(self, path: str = "/") -> List[Dict[str, Any]]:
        items = [item async for item in self.client.listdir(path)]
        return [dict(item) for item in items]

    @handle_yadisk_errors
    async def upload_file(self, local_path: str, remote_path: str):
        await self.client.upload(local_path, remote_path)

    @handle_yadisk_errors
    async def upload_from_stream(self, stream, remote_path: str):
        await self.client.upload(stream, remote_path)

    @handle_yadisk_errors
    async def download_file(self, remote_path: str, local_path: str):

        await self.client.download(remote_path, local_path)

    @handle_yadisk_errors
    async def download_to_stream(self, remote_path: str, stream):
        await self.client.download(remote_path, stream)

    @handle_yadisk_errors
    async def remove_file(self, remote_path: str, permanently: bool = True):
        await self.client.remove(remote_path, permanently=permanently)

    @handle_yadisk_errors
    async def make_dir(self, path: str):
        result = await self.client.mkdir(path)
        return dict(result)

    @handle_yadisk_errors
    async def publish(self, path: str):
        result = await self.client.publish(path)
        return dict(result)

    @handle_yadisk_errors
    async def unpublish(self, path: str):
        result = await self.client.unpublish(path)
        return dict(result)

    @handle_yadisk_errors
    async def get_public_url(self, path: str) -> str:
        meta = await self.client.get_meta(path)
        return meta.public_url if hasattr(meta, "public_url") else None