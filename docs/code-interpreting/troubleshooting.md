# Troubleshooting

## Common Issues

**Timeout Errors**

::: code-group

```python [Python]
result = session.code.run(long_code, "python", timeout_s=600)
```

```typescript [TypeScript]
const result = await session.code.run(longCode, "python", 600);
```

:::

**Memory Issues**

::: code-group

```python [Python]
large_data_code = """
chunk_size = 10000
for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    processed_chunk = chunk.groupby('category').sum()
    print(f"Processed chunk with {len(chunk)} rows")
"""
```

```typescript [TypeScript]
const largeDataCode = `
chunk_size = 10000
for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    processed_chunk = chunk.groupby('category').sum()
    print(f"Processed chunk with {len(chunk)} rows")
`;
```

:::

**Import Errors**

::: code-group

```python [Python]
check_packages = """
import pkg_resources
installed_packages = [d.project_name for d in pkg_resources.working_set]
print("Available packages:", sorted(installed_packages))
"""
session.code.run(check_packages, "python")
```

```typescript [TypeScript]
const checkPackages = `
import pkg_resources
installed_packages = [d.project_name for d in pkg_resources.working_set]
print("Available packages:", sorted(installed_packages))
`;
await session.code.run(checkPackages, "python");
```

:::

**Syntax Errors**

::: code-group

```python [Python]
def validate_python_syntax(code: str) -> bool:
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False

code_to_check = "print('Hello World')"
if validate_python_syntax(code_to_check):
    result = session.code.run(code_to_check, "python")
```

```typescript [TypeScript]
const codeToCheck = "print('Hello World')";
const result = await session.code.run(codeToCheck, "python");
if (!result.success) {
  console.error("Syntax or runtime error:", result.errorMessage);
}
```

:::