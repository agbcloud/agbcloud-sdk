import {
  LogLevel,
  setLogLevel,
  getLogLevel,
  logDebug,
  logInfo,
  logWarn,
  logError,
  maskSensitiveData,
  logApiCall,
  logApiResponse,
  logOperationStart,
  logOperationSuccess,
  logOperationError,
} from "../../src/logger";

describe("Logger", () => {
  let consoleDebugSpy: jest.SpyInstance;
  let consoleInfoSpy: jest.SpyInstance;
  let consoleWarnSpy: jest.SpyInstance;
  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    consoleDebugSpy = jest.spyOn(console, "debug").mockImplementation();
    consoleInfoSpy = jest.spyOn(console, "info").mockImplementation();
    consoleWarnSpy = jest.spyOn(console, "warn").mockImplementation();
    consoleErrorSpy = jest.spyOn(console, "error").mockImplementation();
  });

  afterEach(() => {
    consoleDebugSpy.mockRestore();
    consoleInfoSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
    setLogLevel(LogLevel.INFO);
  });

  describe("LogLevel enum", () => {
    test("DEBUG is 0", () => {
      expect(LogLevel.DEBUG).toBe(0);
    });

    test("INFO is 1", () => {
      expect(LogLevel.INFO).toBe(1);
    });

    test("WARN is 2", () => {
      expect(LogLevel.WARN).toBe(2);
    });

    test("ERROR is 3", () => {
      expect(LogLevel.ERROR).toBe(3);
    });

    test("SILENT is 4", () => {
      expect(LogLevel.SILENT).toBe(4);
    });
  });

  describe("setLogLevel / getLogLevel", () => {
    test("setLogLevel and getLogLevel", () => {
      setLogLevel(LogLevel.DEBUG);
      expect(getLogLevel()).toBe(LogLevel.DEBUG);

      setLogLevel(LogLevel.WARN);
      expect(getLogLevel()).toBe(LogLevel.WARN);

      setLogLevel(LogLevel.SILENT);
      expect(getLogLevel()).toBe(LogLevel.SILENT);
    });
  });

  describe("logDebug", () => {
    test("logs when level <= DEBUG", () => {
      setLogLevel(LogLevel.DEBUG);
      logDebug("test message");
      expect(consoleDebugSpy).toHaveBeenCalled();
      expect(consoleDebugSpy.mock.calls[0][0]).toContain("DEBUG");
      expect(consoleDebugSpy.mock.calls[0][0]).toContain("test message");
    });

    test("does not log when level > DEBUG", () => {
      setLogLevel(LogLevel.INFO);
      logDebug("should not appear");
      expect(consoleDebugSpy).not.toHaveBeenCalled();
    });
  });

  describe("logInfo", () => {
    test("logs when level <= INFO", () => {
      setLogLevel(LogLevel.INFO);
      logInfo("info message");
      expect(consoleInfoSpy).toHaveBeenCalled();
      expect(consoleInfoSpy.mock.calls[0][0]).toContain("INFO");
      expect(consoleInfoSpy.mock.calls[0][0]).toContain("info message");
    });

    test("does not log when level > INFO", () => {
      setLogLevel(LogLevel.WARN);
      logInfo("should not appear");
      expect(consoleInfoSpy).not.toHaveBeenCalled();
    });
  });

  describe("logWarn", () => {
    test("logs when level <= WARN", () => {
      setLogLevel(LogLevel.WARN);
      logWarn("warn message");
      expect(consoleWarnSpy).toHaveBeenCalled();
      expect(consoleWarnSpy.mock.calls[0][0]).toContain("WARN");
      expect(consoleWarnSpy.mock.calls[0][0]).toContain("warn message");
    });

    test("does not log when level > WARN", () => {
      setLogLevel(LogLevel.ERROR);
      logWarn("should not appear");
      expect(consoleWarnSpy).not.toHaveBeenCalled();
    });
  });

  describe("logError", () => {
    test("logs when level <= ERROR", () => {
      setLogLevel(LogLevel.ERROR);
      logError("error message");
      expect(consoleErrorSpy).toHaveBeenCalled();
      expect(consoleErrorSpy.mock.calls[0][0]).toContain("ERROR");
      expect(consoleErrorSpy.mock.calls[0][0]).toContain("error message");
    });

    test("does not log when level is SILENT", () => {
      setLogLevel(LogLevel.SILENT);
      logError("should not appear");
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe("SILENT level", () => {
    test("suppresses all logs", () => {
      setLogLevel(LogLevel.SILENT);
      logDebug("debug");
      logInfo("info");
      logWarn("warn");
      logError("error");
      expect(consoleDebugSpy).not.toHaveBeenCalled();
      expect(consoleInfoSpy).not.toHaveBeenCalled();
      expect(consoleWarnSpy).not.toHaveBeenCalled();
      expect(consoleErrorSpy).not.toHaveBeenCalled();
    });
  });

  describe("maskSensitiveData", () => {
    test("masks api_key field", () => {
      const data = { api_key: "sk-1234567890abcdef" };
      const masked = maskSensitiveData(data) as typeof data;
      expect(masked.api_key).toBe("sk****ef");
    });

    test("masks password field", () => {
      const data = { password: "mySecretPassword123" };
      const masked = maskSensitiveData(data) as typeof data;
      expect(masked.password).toBe("my****23");
    });

    test("masks token field", () => {
      const data = { token: "bearer-abc123xyz" };
      const masked = maskSensitiveData(data) as typeof data;
      expect(masked.token).toBe("be****yz");
    });

    test("leaves non-sensitive fields unchanged", () => {
      const data = { username: "john", email: "john@example.com" };
      const masked = maskSensitiveData(data) as typeof data;
      expect(masked.username).toBe("john");
      expect(masked.email).toBe("john@example.com");
    });

    test("handles arrays", () => {
      const data = [{ api_key: "key12345" }, { api_key: "key67890" }];
      const masked = maskSensitiveData(data) as typeof data;
      expect(masked[0].api_key).toBe("ke****45");
      expect(masked[1].api_key).toBe("ke****90");
    });

    test("handles nested objects", () => {
      const data = {
        config: {
          api_key: "secret-key-123",
          name: "public",
        },
      };
      const masked = maskSensitiveData(data) as typeof data;
      expect(masked.config.api_key).toBe("se****23");
      expect(masked.config.name).toBe("public");
    });

    test("short values get fully masked", () => {
      const data = { api_key: "ab" };
      const masked = maskSensitiveData(data) as typeof data;
      expect(masked.api_key).toBe("****");
    });

    test("custom fields parameter", () => {
      const data = { customSecret: "my-secret-value" };
      const masked = maskSensitiveData(data, ["customsecret"]) as typeof data;
      expect(masked.customSecret).toBe("my****ue");
    });
  });

  describe("logApiCall", () => {
    test("works without error", () => {
      setLogLevel(LogLevel.DEBUG);
      logApiCall("CreateSession");
      expect(consoleDebugSpy).toHaveBeenCalled();
      expect(consoleDebugSpy.mock.calls[0][0]).toContain("API Call");
    });

    test("logs requestData when provided", () => {
      setLogLevel(LogLevel.DEBUG);
      logApiCall("CreateSession", "params={imageId: x}");
      expect(consoleDebugSpy).toHaveBeenCalledTimes(2);
      expect(consoleDebugSpy.mock.calls[1][0]).toContain("params=");
    });
  });

  describe("logApiResponse", () => {
    test("success case", () => {
      setLogLevel(LogLevel.INFO);
      logApiResponse("CreateSession", "req-123", true);
      expect(consoleInfoSpy).toHaveBeenCalled();
      expect(consoleInfoSpy.mock.calls[0][0]).toContain("API Response");
      expect(consoleInfoSpy.mock.calls[0][0]).toContain("RequestId=req-123");
    });

    test("failure case", () => {
      setLogLevel(LogLevel.ERROR);
      logApiResponse("CreateSession", "req-456", false);
      expect(consoleErrorSpy).toHaveBeenCalled();
      expect(consoleErrorSpy.mock.calls[0][0]).toContain("API Response Failed");
    });
  });

  describe("logOperationStart", () => {
    test("works without error", () => {
      setLogLevel(LogLevel.INFO);
      logOperationStart("FileSystem.readFile");
      expect(consoleInfoSpy).toHaveBeenCalled();
      expect(consoleInfoSpy.mock.calls[0][0]).toContain("Starting");
    });

    test("logs details when provided", () => {
      setLogLevel(LogLevel.DEBUG);
      logOperationStart("FileSystem.readFile", "Path=/foo.txt");
      expect(consoleDebugSpy).toHaveBeenCalled();
      expect(consoleDebugSpy.mock.calls[0][0]).toContain("Details");
    });
  });

  describe("logOperationSuccess", () => {
    test("works without error", () => {
      setLogLevel(LogLevel.INFO);
      logOperationSuccess("FileSystem.readFile");
      expect(consoleInfoSpy).toHaveBeenCalled();
      expect(consoleInfoSpy.mock.calls[0][0]).toContain("Completed");
    });

    test("logs result when provided", () => {
      setLogLevel(LogLevel.DEBUG);
      logOperationSuccess("FileSystem.readFile", "RequestId=req-1");
      expect(consoleDebugSpy).toHaveBeenCalled();
      expect(consoleDebugSpy.mock.calls[0][0]).toContain("Result");
    });
  });

  describe("logOperationError", () => {
    test("works without error", () => {
      setLogLevel(LogLevel.ERROR);
      logOperationError("FileSystem.readFile", "File not found");
      expect(consoleErrorSpy).toHaveBeenCalledTimes(2);
      expect(consoleErrorSpy.mock.calls[0][0]).toContain("Failed");
      expect(consoleErrorSpy.mock.calls[1][0]).toContain("File not found");
    });
  });
});
