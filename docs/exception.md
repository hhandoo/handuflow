# 1. Raise a simple exception

```python
from handuflow.exceptions.storage import StorageError
from handuflow.exceptions.errors.storage import StorageErrors

raise StorageError(
    StorageErrors.NOT_FOUND,
    path="/data/customer.csv",
    provider="local",
)
```

Internally this means:

```text
Type      : StorageError

Code      : HF-STORAGE-001

Message   : Storage object does not exist.

Context

path      : /data/customer.csv
provider  : local
```

---

# 2. Wrap another exception

This is the most common usage.

```python
from pathlib import Path

try:
    data = Path(path).read_bytes()

except OSError as ex:
    raise StorageError(
        StorageErrors.READ_FAILED,
        cause=ex,
        path=path,
        provider="local",
    ) from ex
```

Notice the important part

```python
from ex
```

This preserves the original traceback.

---

# 3. Catch only storage exceptions

```python
try:
    storage.read(path)

except StorageError as ex:
    logger.error(ex.to_dict())
```

---

# 4. Catch all Handuflow exceptions

```python
from handuflow.exceptions import HanduflowError

try:
    workflow.run()

except HanduflowError as ex:
    ExceptionHandler.handle(ex)
```

---

# 5. Access structured information

```python
try:
    ...

except StorageError as ex:

    print(ex.code)

    print(ex.message)

    print(ex.context)

    print(ex.cause)
```

Output

```text
HF-STORAGE-001

Storage object does not exist.

{
    "path": "/tmp/a.csv",
    "provider": "local"
}

FileNotFoundError(...)
```

---

# 6. Logging

Your handler later becomes trivial.

```python
def handle(exception: HanduflowError):

    logger.exception(
        exception.message,
        extra=exception.to_dict(),
    )
```

---

# 7. Retry logic

Suppose later you add

```python
recoverable=True
```

inside `ErrorDefinition`.

Then

```python
try:
    ...

except HanduflowError as ex:

    if ex.recoverable:
        retry()

    else:
        raise
```

No need to inspect the exception type.

---

# 8. HTTP API

If Handuflow is used inside a REST API

```python
except HanduflowError as ex:

    return jsonify(ex.to_dict()), 500
```

---

# 9. Databricks

```python
except StorageError as ex:

    spark_logger.error(ex.to_dict())
```

Exactly the same exception object.

---