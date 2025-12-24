# MCP access guide

The AGB platform provides a unified interaction interface between AI models and runtime environments based on the open-source standardized protocol MCP (Model Context Protocol). The platform achieves deep integration with cloud runtime environments, enabling developers to directly access cloud functions such as session management, file operations, command execution, application management, and window control through MCP.

## Prerequisites

Please ensure that you have created an API Key, otherwise you will be missing necessary information in the operation steps. For more operations, please refer to [Create API Key](https://agb.ai/console/overview).

## Steps

### Step 1: Get MCP Address

1. Log in to the AGB console.
2. Click **API Key** in the left navigation bar.
3. On the API Key management page, click **More** in the Actions column of the target API KEY, and select **MCP Address**.
4. In the MCP Address dialog, select one of the following tabs according to your business needs:
   - Linux
   - Browser
   - Code
5. Click **Copy Code**.

Please specify the appropriate image in the `IMAGEID` field of the MCP address according to your business needs. The MCP addresses below are code examples only. Please refer to the code in your console for the actual values. For more information about viewing MCP addresses, please refer to Get MCP Address.

#### Set System Image

##### Code

```json
{
    "mcpServers":{
        "agbcloud_mcp_server":{
            "url":"https://mcp.agb.cloud/sse?APIKEY=ako-**************&IMAGEID=agb-code-space-1"
        }
    }
}
```

##### Browser

```json
{
  "mcpServers": {
    "wuying_mcp_server": {
      "url": "https://mcp.agb.cloud/sse?APIKEY=ako-**************&IMAGEID=agb-browser-use-1"
    }
  }
}
```

##### Linux

```json
{
  "mcpServers": {
    "wuying_mcp_server": {
      "url": "https://mcp.agb.cloud/sse?APIKEY=ako-**************&IMAGEID=agb-computer-use-ubuntu-2204"
    }
  }
}
```

#### Set Specified Image

You can also set the `IMAGEID` field to the image ID of a custom image. After setting, the image corresponding to that image ID will be used.



**Note**

To get the image ID:

Please log in to the AGB console and click **Images**. In **Images**, select the **Custom** tab, then get your target image ID from the image list and replace `<YOUR_IMAGEID>`.

```json
{
  "mcpServers": {
    "wuying_mcp_server": {
      "url": "https://mcp.agb.cloud/sse?APIKEY=ako-**************&IMAGEID=<YOUR_IMAGEID>"
    }
  }
}
```

### Step 2: Configure MCP Service

Add the MCP address code block in MCP-supported tools (such as Cline, Cursor, etc.). The following uses Cursor V2.1.46 as an example.

1. Open the **Cursor Settings** panel, and click **MCP** in the left navigation bar.
2. On the **Tools & MCP** panel, click **Add a Custom MCP server**.
3. Paste the MCP address code block copied from Get MCP Address into the mcp.json file, and save the file to complete the service configuration.
   * Three connection methods are supported: SSE, Stdio, and Streamable. Developers can choose the appropriate connection method according to project requirements.

#### SSE

```json
{
  "mcpServers": {
    "wuying_mcp_server": {
      "url": "https://mcp.agb.cloud/sse?APIKEY=YOUR_API_KEY&IMAGEID=<YOUR_IMAGEID>"
    }
  }
}
```

#### Streamable

```json
{
  "mcpServers": {
    "wuying_mcp_server": {
      "url": "https://mcp.agb.cloud/mcp?APIKEY=YOUR_API_KEY&IMAGEID=<YOUR_IMAGEID>"
    }
  }
}
```

## MCP Tool List

Please refer to the following for MCP Tool list usage and support scope. Please select according to your environment to view more information.

| **Class** | **Description** | **Linux** | **Browser** | **CodeSpace** |
|-----------|-----------------|-----------|-------------|---------------|
| Sessions | The Session class represents a session in the AGB cloud environment. It provides methods for managing file systems, executing commands, and more. | Supported | Supported | Supported |
| Filesystem | The FileSystem class provides methods for file operations in AGB cloud environment sessions, including reading, writing, editing, searching files, and directory operations. | Supported | Supported | Supported |
| UI | The UI class provides methods for interacting with UI elements in the AGB cloud environment. This includes getting UI elements, sending key events, entering text, performing gesture operations, and taking screenshots. | Supported | Not Supported | N/A |
| Application | The Application class provides methods for managing applications in the AGB cloud environment, including listing installed applications, starting applications, and stopping running processes. | Supported | Not Supported | N/A |
| Command | The Command class provides methods for executing commands in AGB cloud environment sessions. | Supported | Supported | Supported |
| CodeSpace | Execute code in the specified programming language and set timeout. | N/A | N/A | Supported |