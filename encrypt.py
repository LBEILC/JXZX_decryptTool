import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import ujson

Executor = ThreadPoolExecutor(max_workers=50, thread_name_prefix="T")


def encode_file(file_path: Path, header_len):
    with file_path.open("rb") as f:
        data = f.read()

    enc_data = data[:header_len]
    with file_path.open("wb") as f:
        f.write(enc_data + data)

    # 确保在字符串末尾没有额外的换行符
    # 默认情况下，print 函数会在输出的字符串末尾添加换行符
    print(f"正在加密文件: {file_path.name}", end="")


def encode(game_bundles_path: Path, cache_file):
    if not game_bundles_path.exists():
        raise FileNotFoundError("游戏bundles目录不存在")

    if not cache_file:
        raise FileNotFoundError("未指定index_cache文件")

    with open(cache_file, "r", encoding="utf-8") as f:
        cache_file_index = ujson.load(f)

    file_list_len = len(os.listdir(game_bundles_path))
    print(f"找到 {file_list_len} 个文件，开始加密...")

    futures = []

    for AssetFile in game_bundles_path.iterdir():
        header_len = cache_file_index.get(AssetFile.name)
        if header_len is None:
            print(f"{AssetFile.name} 加密失败, 未找到索引, 请重新解密后再加密")
            continue
        futures.append(Executor.submit(encode_file, AssetFile, header_len))

    for future in as_completed(futures):
        future.result()  # 我们不需要结果，但这会等待任务完成

    print("加密完成")
