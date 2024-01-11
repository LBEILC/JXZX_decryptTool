import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from binascii import hexlify, unhexlify
import ujson
from datetime import datetime

Executor = ThreadPoolExecutor(max_workers=50, thread_name_prefix="T")
cache_file_index_path = Path("cache_index.json")


def ensure_cache_file_index():
    if not cache_file_index_path.exists():
        with cache_file_index_path.open("w", encoding="utf-8") as f:
            ujson.dump({}, f)


ensure_cache_file_index()

with cache_file_index_path.open("r", encoding="utf-8") as f:
    cache_file_index = ujson.load(f)


def find_next_unityFS_index(file_data: bytes):
    openFileHex = hexlify(file_data)
    unityFX_len = len(re.findall(b"556e6974794653000000000", openFileHex))
    if unityFX_len < 2:
        return -1
    else:
        find_index = len(re.search(b".+556e6974794653000000000", openFileHex).group()) - 23
        return len(unhexlify(openFileHex[:find_index]))


def decrypt_file(file_path: Path):
    with file_path.open("rb") as f:
        data = f.read()

    header_len = find_next_unityFS_index(data)
    if header_len == -1:
        return file_path.name, header_len

    with file_path.open("wb") as f:
        f.write(data[header_len:])

    return file_path.name, header_len


def decrypt(game_bundles_path: Path, progress_callback=None):
    if not game_bundles_path.exists():
        raise FileNotFoundError("游戏bundles目录不存在")

    file_list_len = len(os.listdir(game_bundles_path))

    # 使用 progress_callback 更新进度
    if progress_callback:
        progress_callback(0, file_list_len)

    futures = []

    for AssetFile in game_bundles_path.iterdir():
        futures.append(Executor.submit(decrypt_file, AssetFile))

    decrypt_result = {}
    for i, future in enumerate(as_completed(futures)):
        file_name, header_len = future.result()
        if header_len != -1:
            decrypt_result[file_name] = header_len
        if progress_callback:
            progress_callback(i + 1, file_list_len)

    # 创建 index_cache 文件夹和 index_cache_日期.json 文件
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_folder = Path("index_cache")
    cache_folder.mkdir(exist_ok=True)
    cache_file_path = cache_folder / f"index_cache_{date_str}.json"

    # 将解密结果写入新的 index_cache_日期.json 文件
    with cache_file_path.open("w", encoding="utf-8") as f:
        ujson.dump(decrypt_result, f)

    print("全部完成")
