# Advanced features

## What you’ll do

Enable stealth/fingerprint settings, manage extensions, and handle browser/session lifecycle details for robust automation.

## Prerequisites

- `AGB_API_KEY`
- A valid browser `image_id` (e.g. `agb-browser-use-1`)

## Quickstart

Use stealth + fingerprint configuration:

```python
from agb.modules.browser import BrowserOption, BrowserFingerprint

option = BrowserOption(
    use_stealth=True,
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"],
    ),
)
```

For full fingerprint details, see [`docs/browser/fingerprint.md`](fingerprint.md).

## Common tasks

### Fingerprint

- Enable `use_stealth=True` when using fingerprints.
- See: [`docs/browser/fingerprint.md`](fingerprint.md)

### Extensions (upload / list / update / delete)

```python
from agb.extension import ExtensionsService

extensions_service = ExtensionsService(agb, "my_browser_extensions")
extension = extensions_service.create("/path/to/my-extension.zip")
print("Uploaded extension:", extension.id)

for ext in extensions_service.list():
    print(ext.id, ext.name)
```

See: [`docs/browser/extension.md`](extension.md)

### Load extensions into a session

```python
from agb.session_params import BrowserContext, CreateSessionParams

ext_option = extensions_service.create_extension_option([extension.id])
browser_context = BrowserContext(
    context_id="browser_session_with_extensions",
    auto_upload=True,
    extension_option=ext_option,
)

create_result = agb.create(
    CreateSessionParams(image_id="agb-browser-use-1", browser_context=browser_context)
)
```

### Check browser status / current option

```python
if session.browser.is_initialized():
    print("Browser is ready")

current_option = session.browser.get_option()
if current_option:
    print("Using stealth:", current_option.use_stealth)
```

### Error handling pattern

```python
from agb.exceptions import BrowserError
from agb.modules.browser import BrowserOption

try:
    ok = await session.browser.initialize_async(BrowserOption())
    if not ok:
        raise BrowserError("Failed to initialize browser")
except BrowserError as e:
    print("Browser error:", e)
```

## Best practices

- Keep extensions and fingerprints in their dedicated docs to avoid duplication.
- Prefer internal pages during initialization (see [`docs/browser/configuration.md`](configuration.md)).

## Troubleshooting

### Extension not loaded

- **Likely cause**: missing `extension_path` or missing upload step.
- **Fix**: follow the extension workflow in [`docs/browser/extension.md`](extension.md).

## Related

- Main guide: [`docs/browser/overview.md`](overview.md)
- Configuration: [`docs/browser/configuration.md`](configuration.md)
- Extensions: [`docs/browser/extension.md`](extension.md)
- Fingerprint: [`docs/browser/fingerprint.md`](fingerprint.md)

