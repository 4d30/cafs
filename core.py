import os
import hashlib
from itertools import batched, islice, chain
from typing import Any, Iterable

CAFS_ROOT = '/set/your/cafs_root'

try:
    import msgpack

    def _serializer_dumps(data):
        return msgpack.packb(data, use_bin_type=True)

    def _serializer_loads(data):
        return msgpack.unpackb(data, raw=False)
except ImportError:
    import pickle

    def _serializer_dumps(data):
        return pickle.dumps(data)

    def _serializer_loads(data):
        return pickle.loads(data)

def get_hash(content_bytes: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(content_bytes)
    cid = hasher.hexdigest()
    return cid

def _chunk_string(chunk_width: int, iterable: Iterable):
    all_chunks = zip(*[iterable] * chunk_width)
    joined = map(''.join, all_chunks)
    yield from joined

def _get_cid_path(root_path: str, cid: str) -> str:
    """Calculates the chunked path for a given CID

    SHARD POWER/WIDTH&DEPTH CALCULATION

    spse 6 ATS, 1,500 companies each, with 200 jobs
        let
            n_records = 6*1,500*200 = 1,800,000 records
    ext4 CAN handle ~4 giga records/node and we'll target 10,000
        let
            nodes/leaf = 10,000  records/node
    for performance over capacity.
        then
            required leaves = 1,800,000/10,000 = 18,000 leaves
    given sha256 hash is base-16
    solve min required shard power p
        then
            min(p) st 16^p > 18,000
        solve for p
            p = 4 -> 16^4 = 65,536 > 18,000
        finally
            +-------+
            | p = 4 |
            +-------+
    depth x width = p
    choose (2 x 2) to balance traversal cost and directory load
    """
    chunk_width = 2
    chunk_depth = 2
    if len(cid) < chunk_width:
        raise ContentStoreError('too short for chunking.')
    cid_chunks = _chunk_string(chunk_width, iter(cid))
    cid_chunks = islice(cid_chunks, chunk_depth)
    path = os.path.join(root_path, *cid_chunks, cid)
    return path


def put(json_obj: dict[str, Any], cafs_root=CAFS_ROOT) -> str:
    """
    Stores a serializable object in a CAFS.

    Args:
        obj: a serializable object
        cafs_root: storage root directory

        Returns:
            str: The content id  of the stored object.
    """
    content_bytes = _serializer_dumps(json_obj)
    cid = get_hash(content_bytes)
    path = _get_cid_path(cafs_root, cid)
    os.makedirs(os.path.dirname(path), mode=504, exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'wb') as handle:
            handle.write(content_bytes)
    os.chmod(path, 288)
    return cid

def get(content_id: str, cafs_root=CAFS_ROOT) -> dict[str, Any]:
    path = _get_cid_path(cafs_root, content_id)
    if os.path.exists(path):
        with open(path, 'rb') as handle:
            obj = _serializer_loads(handle.read())
            return obj
    return None

def _is_empty(directory):
    contents = os.scandir(directory)
    return not any(contents)

def delete(content_id: str, cafs_root=CAFS_ROOT) -> None:
    path = _get_cid_path(cafs_root, content_id)
    if not os.path.exists(path):
        pass  # postinserted
    os.unlink(path)
    return None

def kill_root(cafs_root=CAFS_ROOT):
    # 1. Expand path and perform safety checks
    target = os.path.abspath(cafs_root)

    # Safety: Don't allow short paths or system roots
    if len(target) < 10 or target.count('/') < 3: 
        raise PermissionError(f"Path '{target}' is too shallow. Potential safety risk.")

    if not os.path.isdir(target):
        return

    # 2. Walk the tree bottom-up
    # 
    for root, dirs, files in os.walk(target, topdown=False):
        # Delete all files in the current directory
        for name in files:
            file_path = os.path.join(root, name)
            os.remove(file_path)

        # Delete all sub-directories in the current directory
        for name in dirs:
            dir_path = os.path.join(root, name)
            os.rmdir(dir_path)

