# CAFS (Content Addressable File System)
This Python module provides a simple Content Addressable File System (CAFS) implementation for storing and retrieving serialized objects. It uses a content ID (CID) based on SHA-256 hash for efficient file storage and retrieval. It optionally uses `msgpack` for serialization; otherwise, it can use pickle.

## Features
 - Store objects: Serialize and store Python objects in a content-addressable way.
 - Retrieve objects: Fetch stored objects by their content ID.
 - Delete objects: Remove stored objects from the system.
 - Clean-up: Safely delete files and directories from the root storage path.

## Depends
 - `msgpack` (optional)

## Installation

To install `msgpack`(optional):
```shell
pip install msgpack
```

## Usage
### Storing an Object
```python
from cafs import put

data = {"name": "example", "value": 42}
cid = put(data)
print(f"Object stored with CID: {cid}")
```

### Retrieving an Object
```python
from cafs import get

cid = "your_content_id_here"
retrieved_data = get(cid)
print(f"Retrieved data: {retrieved_data}")
```

### Deleting an Object
```python
from cafs import delete

cid = "your_content_id_here"
delete(cid)
print(f"Object with CID {cid} deleted")
```

### Cleaning the Root Directory
```python
from cafs import kill_root

kill_root()  # Caution: This will delete all content in the CAFS root.
```

## Functions
 - put(json_obj: dict, cafs_root=CAFS_ROOT) -> str: Stores a serializable object in the CAFS and returns the content ID (CID).
 - get(content_id: str, cafs_root=CAFS_ROOT) -> dict: Retrieves the object associated with the given content ID.
 - delete(content_id: str, cafs_root=CAFS_ROOT) -> None: Deletes the object associated with the given content ID.
 - kill_root(cafs_root=CAFS_ROOT): Deletes all files and directories recursively in the CAFS root directory.

## Configuration
CAFS_ROOT: The root directory for storing content. This can be customized when calling put, get, delete, or kill_root.

## Error Handling
ContentStoreError: Raised when attempting to chunk a content ID that's too short.

## Safety
The kill_root function includes a safety check to ensure it doesn’t accidentally delete system-critical files. It performs path validation before proceeding with deletion.

## Notes
 - Chunking: The module splits content IDs into chunks to create a hierarchical directory structure, optimizing file traversal and access.
 - File Permissions: It sets restrictive file permissions to prevent unauthorized access.


