# Class: Computer

## 📖 Related Tutorial

- [Computer Automation Guide](../../../computer/overview.md) - Complete guide to computer UI automation and control

## Overview

The Computer module provides computer UI automation via sub-modules: `session.computer.mouse`, `session.computer.keyboard`, `session.computer.window`, `session.computer.app`, and `session.computer.screen`. Use these for mouse operations, keyboard input, window management, application control, and screen capture. Legacy flat methods on `session.computer` (e.g. `click_mouse`, `screenshot`) are deprecated; see CHANGES.md for the full API mapping.


## Requirements

- Requires appropriate system permissions for UI automation
- May require specific desktop environment configuration

Computer module for desktop automation. Use sub-modules: mouse, keyboard, window, app, screen.

## Table of contents


### Properties


### Methods

- [keyPress](#keypress)
- [mouseClick](#mouseclick)
- [screenshot](#screenshot)
- [toJSON](#tojson)

## Properties

```typescript
app: ``ApplicationManager``
keyboard: ``KeyboardController``
mouse: ``MouseController``
screen: ``ScreenController``
window: ``WindowManager``
```


## Methods

### keyPress

▸ **keyPress**(`key`): `Promise`\&lt;``BoolResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `key` | `string` |

#### Returns

`Promise`\&lt;``BoolResult``\&gt;

**`Deprecated`**

Use computer.keyboard.press() instead

___

### mouseClick

▸ **mouseClick**(`x`, `y`, `button?`): `Promise`\&lt;``BoolResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `x` | `number` |
| `y` | `number` |
| `button?` | ``MouseButton`` |

#### Returns

`Promise`\&lt;``BoolResult``\&gt;

**`Deprecated`**

Use computer.mouse.click() instead

___

### screenshot

▸ **screenshot**(): `Promise`\&lt;``OperationResult``\&gt;

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

**`Deprecated`**

Use computer.screen.capture() instead

___

### toJSON

▸ **toJSON**(): `Record`\&lt;`string`, `unknown`\&gt;

#### Returns

`Record`\&lt;`string`, `unknown`\&gt;

## Best Practices

1. Use appropriate timeouts for window operations
2. Take screenshots for debugging and verification
3. Handle coordinate calculations properly for different screen resolutions
4. Verify window existence before attempting window operations
5. Use proper key combinations and timing for keyboard operations
6. Clean up application processes after automation tasks
7. Handle application startup and shutdown gracefully


## Related Resources

- [Session API Reference](../session.md)

