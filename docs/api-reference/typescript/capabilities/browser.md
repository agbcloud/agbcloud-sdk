# Class: Browser

## 📖 Related Tutorial

- [Browser Automation Guide](../../../browser/overview.md) - Complete guide to browser automation

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation,
element interaction, screenshot capture, and content extraction. It enables automated testing
and web scraping workflows with support for proxy configuration, fingerprinting, and stealth mode.


## Requirements

- Requires `agb-browser-use-1` image for browser automation features

Browser module for web automation: navigate, click, type, screenshot, and extract content.
Requires initialization with browser options (e.g. stealth, viewport, fingerprint). Use session.browser.agent for high-level tasks.

## Hierarchy

- ``BaseService``

  ↳ **`Browser`**

## Table of contents


### Properties

- [session](#session)

### Methods

- [callMcpTool](#callmcptool)
- [destroy](#destroy)
- [handleError](#handleerror)
- [initialize](#initialize)
- [initializeAsync](#initializeasync)
- [isInitialized](#isinitialized)
- [screenshot](#screenshot)
- [toJSON](#tojson)

## Properties

```typescript
agent: ``BrowserAgent``
```


### session

• `Protected` **session**: ``SessionLike``

#### Inherited from

`BaseService`.`session`

## Methods

### callMcpTool

▸ **callMcpTool**(`name`, `args`, `readTimeout?`, `connectTimeout?`): `Promise`\&lt;``OperationResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `name` | `string` |
| `args` | `Record`\&lt;`string`, `unknown`\&gt; |
| `readTimeout?` | `number` |
| `connectTimeout?` | `number` |

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

#### Inherited from

`BaseService`.`callMcpTool`

___

### destroy

▸ **destroy**(): `Promise`\&lt;``BoolResult``\&gt;

#### Returns

`Promise`\&lt;``BoolResult``\&gt;

### handleError

▸ **handleError**(`e`): `unknown`

#### Parameters

| Name | Type |
| :------ | :------ |
| `e` | `unknown` |

#### Returns

`unknown`

#### Inherited from

`BaseService`.`handleError`

___

### initialize

▸ **initialize**(`option`): `Promise`\&lt;`boolean`\&gt;

Initialize the browser instance with the given options.

Note: In Python, initialize() uses sync HTTP and initialize_async() uses async HTTP.
In TypeScript there is no standard synchronous HTTP API; both methods use the same
async client and return Promise&lt;boolean&gt;. Use initialize() or initializeAsync()
interchangeably (e.g. await session.browser.initialize(option)).

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `option` | ``BrowserOption`` \| ``BrowserOptionClass`` | Browser configuration options (BrowserOptionClass or plain BrowserOption). |

#### Returns

`Promise`\&lt;`boolean`\&gt;

Promise resolving to true if initialization succeeded, false otherwise.

___

### initializeAsync

▸ **initializeAsync**(`option`): `Promise`\&lt;`boolean`\&gt;

Initialize the browser instance asynchronously.
Same as initialize() in TypeScript (both use async HTTP). Exists for API parity with
Python SDK where initialize_async uses async HTTP and initialize uses sync HTTP.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `option` | ``BrowserOption`` \| ``BrowserOptionClass`` | Browser configuration options (BrowserOptionClass or plain BrowserOption). |

#### Returns

`Promise`\&lt;`boolean`\&gt;

Promise resolving to true if initialization succeeded, false otherwise.

___

### isInitialized

▸ **isInitialized**(): `boolean`

#### Returns

`boolean`

___

### screenshot

▸ **screenshot**(`page`, `fullPage?`, `options?`): `Promise`\&lt;`Uint8Array`\&gt;

Takes a screenshot of the specified Playwright page with enhanced options.
Handles scroll-to-load for lazy content, lazy images, and viewport resizing.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `page` | `unknown` | `undefined` | The Playwright Page object to screenshot. |
| `fullPage` | `boolean` | `false` | Whether to capture the full scrollable page. Defaults to false. |
| `options` | `Record`\&lt;`string`, `unknown`\&gt; | `{}` | Additional screenshot options (type, quality, timeout, etc.). |

#### Returns

`Promise`\&lt;`Uint8Array`\&gt;

Screenshot data as Uint8Array.

**`Throws`**

If browser is not initialized.

___

### toJSON

▸ **toJSON**(): `Record`\&lt;`string`, `unknown`\&gt;

#### Returns

`Record`\&lt;`string`, `unknown`\&gt;

#### Inherited from

`BaseService`.`toJSON`

## Best Practices

1. Initialize browser with appropriate options before use
2. Wait for page load completion before interacting with elements
3. Use appropriate selectors (CSS, XPath) for reliable element identification
4. Handle navigation timeouts and errors gracefully
5. Take screenshots for debugging and verification
6. Clean up browser resources after automation tasks
7. Configure proxy settings properly for network requirements


## Related Resources

- [Session API Reference](../session.md)

