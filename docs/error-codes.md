# Error Code Dictionary

All HanduFLOW errors use a stable code in the format `HF-{CATEGORY}-{NUMBER}`.
Each code maps to a dedicated exception class that inherits from `HanduFlowException`.

## Categories

| Category | Code prefix | Base exception |
| --- | --- | --- |
| storage | `HF-STORAGE-` | `HanduFlowStorageException` |
| logging | `HF-LOGGING-` | `HanduFlowLoggingException` |
| configuration | `HF-CONFIG-` | `HanduFlowConfigurationException` |
| workflow | `HF-WORKFLOW-` | `HanduFlowWorkflowException` |
| validation | `HF-VALIDATION-` | `HanduFlowValidationException` |
| system | `HF-SYSTEM-` | `HanduFlowSystemException` |

## Full registry

| Code | Category | Exception class | Message |
| --- | --- | --- | --- |
| `HF-CONFIG-001` | configuration | `ConfigurationFileNotFoundError` | Configuration file not found |
| `HF-CONFIG-002` | configuration | `ConfigurationInvalidError` | Configuration file is invalid |
| `HF-CONFIG-003` | configuration | `ConfigurationKeyMissingError` | Required configuration key is missing |
| `HF-CONFIG-004` | configuration | `ConfigurationValueInvalidError` | Configuration value is invalid |
| `HF-CONFIG-005` | configuration | `ConfigurationSectionMissingError` | Configuration section is missing |
| `HF-CONFIG-006` | configuration | `ConfigurationLoadError` | Failed to load configuration |
| `HF-CONFIG-007` | configuration | `ConfigurationSaveError` | Failed to save configuration |
| `HF-CONFIG-008` | configuration | `ConfigurationTypeMismatchError` | Configuration type mismatch |
| `HF-CONFIG-009` | configuration | `ConfigurationEnvironmentError` | Configuration environment override failed |
| `HF-CONFIG-010` | configuration | `ConfigurationSchemaValidationError` | Configuration schema validation failed |
| `HF-LOGGING-001` | logging | `LoggingConfigurationError` | Failed to configure logger |
| `HF-LOGGING-002` | logging | `LoggingDirectoryNotWritableError` | Log directory is not writable |
| `HF-LOGGING-003` | logging | `LoggingWriteError` | Failed to write log record |
| `HF-LOGGING-004` | logging | `LoggingRotationError` | Failed to rotate log file |
| `HF-LOGGING-005` | logging | `LoggingInvalidLevelError` | Invalid log level |
| `HF-LOGGING-006` | logging | `LoggingPurgeError` | Log retention purge failed |
| `HF-LOGGING-007` | logging | `LoggingHandlerNotConfiguredError` | Logger handler is not configured |
| `HF-LOGGING-008` | logging | `LoggingInvalidFileNameError` | Log file name is invalid |
| `HF-LOGGING-009` | logging | `LoggingConsoleUnavailableError` | Console logging is unavailable |
| `HF-LOGGING-010` | logging | `LoggingFormatError` | Log formatting failed |
| `HF-STORAGE-001` | storage | `StoragePathNotFoundError` | Storage path does not exist |
| `HF-STORAGE-002` | storage | `StoragePathExistsError` | Storage path already exists |
| `HF-STORAGE-003` | storage | `StorageNotAFileError` | Storage path is not a file |
| `HF-STORAGE-004` | storage | `StorageNotADirectoryError` | Storage path is not a directory |
| `HF-STORAGE-005` | storage | `StorageReadError` | Failed to read storage object |
| `HF-STORAGE-006` | storage | `StorageWriteError` | Failed to write storage object |
| `HF-STORAGE-007` | storage | `StorageDeleteError` | Failed to delete storage object |
| `HF-STORAGE-008` | storage | `StorageMoveError` | Failed to move storage object |
| `HF-STORAGE-009` | storage | `StorageCopyError` | Failed to copy storage object |
| `HF-STORAGE-010` | storage | `StorageListError` | Failed to list storage directory |
| `HF-STORAGE-011` | storage | `StorageProviderNotConfiguredError` | Storage provider is not configured |
| `HF-STORAGE-012` | storage | `StorageProviderUnsupportedError` | Unsupported storage provider |
| `HF-STORAGE-013` | storage | `StoragePermissionDeniedError` | Storage permission denied |
| `HF-STORAGE-014` | storage | `StorageTimeoutError` | Storage operation timed out |
| `HF-STORAGE-015` | storage | `StorageInvalidPathError` | Invalid storage path |
| `HF-SYSTEM-001` | system | `SystemUnhandledExceptionError` | Unhandled system exception |
| `HF-SYSTEM-002` | system | `SystemInternalError` | Internal system error |
| `HF-SYSTEM-003` | system | `SystemResourceUnavailableError` | System resource unavailable |
| `HF-SYSTEM-004` | system | `SystemInitializationError` | System initialization failed |
| `HF-SYSTEM-005` | system | `SystemShutdownError` | System shutdown failed |
| `HF-SYSTEM-006` | system | `SystemDependencyError` | System dependency failed |
| `HF-SYSTEM-007` | system | `SystemTimeoutError` | System operation timed out |
| `HF-SYSTEM-008` | system | `SystemConcurrencyError` | System concurrency error |
| `HF-SYSTEM-009` | system | `SystemSerializationError` | System serialization failed |
| `HF-SYSTEM-010` | system | `SystemDeserializationError` | System deserialization failed |
| `HF-VALIDATION-001` | validation | `ValidationFailedError` | Validation failed |
| `HF-VALIDATION-002` | validation | `ValidationRequiredFieldMissingError` | Required field is missing |
| `HF-VALIDATION-003` | validation | `ValidationInvalidTypeError` | Field type is invalid |
| `HF-VALIDATION-004` | validation | `ValidationOutOfRangeError` | Field value is out of range |
| `HF-VALIDATION-005` | validation | `ValidationInvalidFormatError` | Field format is invalid |
| `HF-VALIDATION-006` | validation | `ValidationSchemaError` | Schema validation failed |
| `HF-VALIDATION-007` | validation | `ValidationConstraintViolationError` | Constraint violation |
| `HF-VALIDATION-008` | validation | `ValidationDuplicateValueError` | Duplicate value detected |
| `HF-VALIDATION-009` | validation | `ValidationCrossFieldError` | Cross-field validation failed |
| `HF-VALIDATION-010` | validation | `ValidationContextInvalidError` | Validation context is invalid |
| `HF-WORKFLOW-001` | workflow | `WorkflowInvalidDefinitionError` | Workflow definition is invalid |
| `HF-WORKFLOW-002` | workflow | `WorkflowStepFailedError` | Workflow step failed |
| `HF-WORKFLOW-003` | workflow | `WorkflowCycleDetectedError` | Workflow dependency cycle detected |
| `HF-WORKFLOW-004` | workflow | `WorkflowStepNotFoundError` | Workflow step not found |
| `HF-WORKFLOW-005` | workflow | `WorkflowTimeoutError` | Workflow execution timed out |
| `HF-WORKFLOW-006` | workflow | `WorkflowCancelledError` | Workflow was cancelled |
| `HF-WORKFLOW-007` | workflow | `WorkflowInvalidStateTransitionError` | Workflow state transition is invalid |
| `HF-WORKFLOW-008` | workflow | `WorkflowArtifactMissingError` | Workflow artifact is missing |
| `HF-WORKFLOW-009` | workflow | `WorkflowSchedulerError` | Workflow scheduler failed |
| `HF-WORKFLOW-010` | workflow | `WorkflowRetryLimitExceededError` | Workflow retry limit exceeded |

## Usage

```python
from handuflow.platform.exceptions import StoragePathNotFoundError, raise_for_code

raise StoragePathNotFoundError(path="/tmp/missing.txt")
raise_for_code("HF-CONFIG-003", details={"key": "log_retention_days"})
```
