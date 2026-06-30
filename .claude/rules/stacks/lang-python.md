# Python Rules

**Applies when:** editing Python (`.py`).

Source: GENERAL_CLAUDE.md § Language & Type Safety Rules.

## Universal (apply here too)

**Forbidden:** bare except, mutable default args, debug prints in production, unchecked env access.

**Required:** type hints on public functions, schema validation for config/requests.

## Enforcement

- mypy, pyright, or ruff for type checking
- Pydantic or equivalent for config and request validation
- Explicit error handling — never swallow exceptions

## Example

```python
def find_user_by_id(user_id: str) -> UserDto | None:
    ...
```

Never: `f"SELECT * FROM users WHERE id = {id}"` without parameterization.
