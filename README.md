
# FlexiStore

**FlexiStore** is a lightweight, cloud-agnostic Python storage abstraction library that provides a simple, unified interface to common file operations (upload, download, list, delete) across different cloud providers. It ships with an Azure Blob implementation out of the box but can be extended to support AWS S3, Google Cloud Storage, and others.

## Features

- **Unified API** for upload/download/list/delete operations.
- **Pluggable backends**: Implement `StorageManager` to add new providers.
- **Minimal dependencies**: Only requires the SDK for the backend you use.
- **CLI tool**: Interactive command-line interface for common operations.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/prakhara56/FlexiStore.git@main
```

Or add to your `requirements.txt`:

```
git+https://github.com/prakhara56/FlexiStore.git@main#egg=flexistore
```

## Quick Start

### As a library

```python
from flexistore.azure import AzureStorageManager

# Initialize with your connection string and container
mgr = AzureStorageManager(conn_str="<AZURE_CONN_STRING>", container="my-container")

# Upload a local file
mgr.upload_file("./data/report.csv", "backups/report.csv")
```

### As a CLI

```bash
# Ensure env vars or .env contain AZURE_CONN_STRING and AZURE_CONTAINER
flexistore-cli
```

Follow the interactive prompts to upload, list, download, or delete blobs.

## API Reference

### `StorageManager` (abstract)

- `upload_file(local_path: str, remote_path: str) -> None`
- `download_file(remote_path: str, local_path: str) -> None`
- `list_files(remote_prefix: str) -> List[str]`
- `download_folder(remote_prefix: str, local_dir: str) -> None`
- `delete_file(remote_path: str) -> None`

### `AzureStorageManager`

Concrete implementation using Azure Blob Storage with built-in error handling.

## CLI Reference

The `flexistore-cli` entry point runs the interactive CLI defined in `cli.py`.

## Extending for Other Providers

1. Create a new class inheriting `StorageManager`.
2. Implement the five methods using your chosen SDK (e.g., boto3 for S3).
3. Add your backend to `__init__.py` for easy imports.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request.

## License

This project is licensed under the MIT License.