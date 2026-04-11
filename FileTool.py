"""
文件操作工具集

提供下载、解压、压缩、查找、读写等常用文件操作。
"""

import asyncio
import gzip
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import httpx
from httpx import AsyncHTTPTransport


async def file_download(
    url, root_dir, file_name=None, timeout=30.0, retries=3, chunk_size=8192
):
    """
    支持断点续传的异步下载。

    Args:
        url: 下载链接
        root_dir: 保存目录
        file_name: 文件名（可选，默认从 URL 提取）
        timeout: 请求超时时间（秒）
        retries: 请求重试次数
        chunk_size: 下载块大小

    Returns:
        下载成功返回文件路径，失败返回 None

    Example:
        >>> await file_download('https://example.com/file.zip', 'downloads/')
        >>> await file_download('https://example.com/file.zip', 'downloads/', file_name='my_file.zip')
    """
    root_dir = Path(root_dir)
    root_dir.mkdir(parents=True, exist_ok=True)

    file_name = Path(file_name) if file_name else Path(urlparse(url).path).name
    save_path = root_dir / file_name

    existing_size = save_path.stat().st_size if save_path.exists() else 0
    headers = {"Range": f"bytes={existing_size}-"} if existing_size else {}

    try:
        transport = AsyncHTTPTransport(retries=retries)
        async with httpx.AsyncClient(transport=transport) as client:
            async with client.stream(
                "GET", url, headers=headers, timeout=timeout, follow_redirects=True
            ) as response:
                if response.status_code == 416:
                    print(f"文件已完整下载: {save_path}")
                    return save_path

                if response.status_code == 206:
                    remaining = int(response.headers.get("content-length", 0))
                    total = remaining + existing_size
                elif response.status_code == 200:
                    total = int(response.headers.get("content-length", 0))
                    existing_size = 0
                else:
                    print(f"下载失败: {response.status_code}")
                    return None

                mode = "ab" if existing_size else "wb"
                with open(save_path, mode) as f:
                    print(f"下载中: {file_name}...")
                    downloaded = existing_size
                    async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            percent = downloaded / total * 100
                            print(
                                f"\r进度: {downloaded}/{total} ({percent:.1f}%)",
                                end="",
                                flush=True,
                            )

                print(f"\n下载完成: {save_path}")
                return save_path

    except httpx.TimeoutException:
        print(f"请求超时: {url}")
    except httpx.ConnectError:
        print(f"连接失败: {url}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP 错误: {e.response.status_code}")
    except httpx.RequestError as e:
        print(f"请求异常: {e}")

    return None


async def file_download_batch(
    urls, root_dir, file_names=None, max_concurrent=5, **kwargs
):
    """
    批量并发下载多个文件。

    Args:
        urls: 下载链接列表
        root_dir: 保存目录
        file_names: 文件名列表（可选，默认从 URL 提取）
        max_concurrent: 最大并发数（默认 5）
        **kwargs: 传递给 download 的参数

    Returns:
        dict: {url: Path 或 None}

    Example:
        >>> results = await file_download_batch(['url1', 'url2'], 'downloads/')
        >>> results = await file_download_batch(['url1', 'url2'], 'downloads/', file_names=['a.zip', 'b.zip'])
    """
    if file_names is None:
        file_names = [None] * len(urls)
    assert len(file_names) == len(urls), "urls 和 file_names 长度必须一致"

    semaphore = asyncio.Semaphore(max_concurrent)

    async def download_one(url, file_name):
        async with semaphore:
            return await file_download(url, root_dir, file_name, **kwargs)

    tasks = [download_one(url, file_name) for url, file_name in zip(urls, file_names)]
    results = await asyncio.gather(*tasks)

    return {url: result for url, result in zip(urls, results)}


def file_extract(file_path, extract_to_dir=None):
    """
    解压压缩文件。

    Args:
        file_path: 压缩文件路径
        extract_to_dir: 解压目录（默认为同名目录）

    Returns:
        解压后的文件/目录路径

    Example:
        >>> extract('downloads/file.zip')
        >>> extract('downloads/file.tar.gz', 'output/')
    """
    file_path = Path(file_path)
    suffix = file_path.suffix
    suffixes = file_path.suffixes

    print(f"解压中: {file_path.name}...")

    if suffix == ".gz" and len(suffixes) == 1:
        output_path = file_path.parent / file_path.stem
        with gzip.open(file_path, "rb") as f_in:
            with open(output_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"解压完成: {output_path}")
        return output_path

    extract_to_dir = (
        Path(extract_to_dir) if extract_to_dir else file_path.parent / file_path.stem
    )
    extract_to_dir.mkdir(parents=True, exist_ok=True)

    if suffix == ".zip":
        with zipfile.ZipFile(file_path, "r") as zip_file:
            zip_file.extractall(extract_to_dir)
    elif suffix == ".tgz" or (len(suffixes) >= 2 and "".join(suffixes) == ".tar.gz"):
        with tarfile.open(file_path, "r:gz") as tar_file:
            tar_file.extractall(extract_to_dir)
    else:
        print(f"不支持的格式: {file_path}")
        return None

    print(f"解压完成: {extract_to_dir}")
    return extract_to_dir


async def file_download_and_extract(url, output_dir, file_name=None, remove=True):
    """
    下载并解压。

    Args:
        url: 下载链接
        output_dir: 输出目录
        file_name: 文件名（可选）
        remove: 是否删除压缩包

    Returns:
        解压后的目录路径

    Example:
        >>> await file_download_and_extract('https://example.com/data.zip', 'data/')
    """
    if remove:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = await file_download(url, tmp_dir, file_name)
            if tmp_path:
                return file_extract(tmp_path, output_dir)
    else:
        file_path = await file_download(url, output_dir, file_name)
        if file_path:
            return file_extract(file_path, output_dir)

    return None


def file_find(dir, extensions=None, recursive=False):
    """
    查找目录下的文件。

    Args:
        dir: 搜索目录
        extensions: 文件扩展名列表，如 ['.py', '.txt']
        recursive: 是否递归搜索

    Yields:
        文件路径

    Example:
        >>> list(find('src/', extensions=['.py']))
        >>> list(find('src/', recursive=True))
    """
    dir = Path(dir)
    if not dir.exists():
        return iter(())

    glob_func = dir.rglob if recursive else dir.glob

    if extensions:
        exts = set(extensions)
        return (f for f in glob_func("*") if f.is_file() and f.suffix in exts)

    return (f for f in glob_func("*") if f.is_file())


def file_read(path, default="", mode="text"):
    """
    读取文件。

    Args:
        path: 文件路径
        default: 文件不存在时的默认值
        mode: 'text' 或 'bytes'

    Returns:
        文件内容

    Example:
        >>> content = read('config.json')
        >>> data = read('data.bin', mode='bytes')
    """
    p = Path(path)
    if not p.exists():
        return default

    if mode == "bytes":
        return p.read_bytes()
    return p.read_text(encoding="utf-8")


def file_write(path, content, encoding="utf-8", mode="text"):
    """
    写入文件。

    Args:
        path: 文件路径
        content: 文件内容
        encoding: 编码
        mode: 'text' 或 'bytes'

    Returns:
        写入的字节数

    Example:
        >>> write('output.txt', 'Hello World')
        >>> write('data.bin', b'\\x00\\x01', mode='bytes')
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if mode == "bytes":
        return p.write_bytes(content)
    return p.write_text(content, encoding=encoding)


def file_size(path, human_readable=True):
    """
    获取文件/目录大小。

    Args:
        path: 文件/目录路径
        human_readable: 是否返回可读格式

    Returns:
        大小（字节或可读字符串）

    Example:
        >>> size('downloads/')
        '1.5 GB'
        >>> size('file.txt', human_readable=False)
        1024
    """
    p = Path(path)

    if p.is_file():
        s = p.stat().st_size
    else:
        s = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())

    if human_readable:
        for unit in ["B", "KB", "MB", "GB"]:
            if s < 1024:
                return f"{s:.1f} {unit}"
            s /= 1024
        return f"{s:.1f} TB"

    return s


def file_compress(obj, output_file, fmt="zip"):
    """
    压缩文件/目录。

    Args:
        obj: 文件/目录路径或路径列表
        output_file: 输出文件路径
        fmt: 压缩格式 ('zip', 'tgz', 'tar.gz')

    Returns:
        压缩文件路径

    Example:
        >>> compress('src/', 'src.zip')
        >>> compress(['file1.txt', 'file2.txt'], 'files.tar.gz', fmt='tar.gz')
    """
    if fmt not in ("zip", "tgz", "tar.gz"):
        raise NotImplementedError(f"不支持 {fmt} 压缩，只支持 zip, tgz, tar.gz")

    obj = [Path(f) for f in obj] if isinstance(obj, (list, tuple)) else [Path(obj)]

    if fmt == "zip":
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in obj:
                if p.is_file():
                    zf.write(p, p.name)
                else:
                    for f in filter(Path.is_file, p.rglob("*")):
                        zf.write(f, f.relative_to(p))
    else:
        with tarfile.open(output_file, "w:gz") as tf:
            for p in obj:
                tf.add(p, arcname=p.name)

    return Path(output_file)


def file_copy(src, dst):
    """
    复制文件/目录。

    Args:
        src: 源文件/目录路径
        dst: 目标文件/目录路径

    Returns:
        目标文件/目录路径

    Example:
        >>> copy('src.txt', 'dst.txt')
        >>> copy('src_dir/', 'dst_dir/')
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if Path(src).is_file():
        shutil.copy2(src, dst)
    else:
        shutil.copytree(src, dst)
    return dst


def file_move(src, dst):
    """
    移动文件/目录。

    Args:
        src: 源文件/目录路径
        dst: 目标文件/目录路径

    Returns:
        目标文件/目录路径

    Example:
        >>> move('old.txt', 'new.txt')
        >>> move('old_dir/', 'new_dir/')
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dst)
    return dst


def file_delete(obj):
    """
    删除文件/目录。

    Args:
        obj: 文件/目录路径或路径列表

    Example:
        >>> delete('temp.txt')
        >>> delete(['file1.txt', 'file2.txt'])
        >>> delete('temp_dir/')
    """
    paths = [Path(f) for f in obj] if isinstance(obj, (list, tuple)) else [Path(obj)]
    for p in paths:
        if p.is_file():
            p.unlink(missing_ok=True)
        elif p.is_dir():
            shutil.rmtree(p)
