import {
    BaseService,
    type SessionLike,
} from "../../api/base-service";
import type {
    BoolResult,
    CursorPosition,
    OperationResult,
    ScreenSize,
    ScreenshotResult,
    WindowListResult,
    WindowInfoResult,
    AppOperationResult,
    ProcessListResult,
    InstalledAppListResult,
    WindowInfo,
    ProcessInfo,
    InstalledAppInfo,
} from "../../types/api-response";
import {
    logOperationStart,
    logOperationSuccess,
    logOperationError,
} from "../../logger";
import { ScreenError } from "../../exceptions";

export enum MouseButton {
    LEFT = "left",
    RIGHT = "right",
    MIDDLE = "middle",
    DOUBLE_LEFT = "double_left",
}

export enum ScrollDirection {
    UP = "up",
    DOWN = "down",
    LEFT = "left",
    RIGHT = "right",
}

function parseBoolResult(
    result: OperationResult,
    requestId: string
): BoolResult {
    const data =
        result.data === "true" ||
        result.data === true ||
        (typeof result.data === "string" &&
            result.data.toLowerCase() === "true");
    return {
        requestId,
        success: result.success,
        data: result.success ? data : false,
        errorMessage: result.errorMessage,
    };
}

export class MouseController extends BaseService {
    async click(
        x: number,
        y: number,
        button: MouseButton = MouseButton.LEFT
    ): Promise<BoolResult> {
        const buttonStr =
            typeof button === "string" ? button : (button as MouseButton);
        logOperationStart("MouseController.click", `X=${x}, Y=${y}, Button=${buttonStr}`);
        const result = await this.callMcpTool("click_mouse", {
            x,
            y,
            button: buttonStr,
        });
        if (result.success) {
            logOperationSuccess(
                "MouseController.click",
                `X=${x}, Y=${y}, Button=${buttonStr}, RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "MouseController.click",
                result.errorMessage ?? "Failed to click mouse"
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async move(x: number, y: number): Promise<BoolResult> {
        logOperationStart("MouseController.move", `X=${x}, Y=${y}`);
        const result = await this.callMcpTool("move_mouse", { x, y });
        if (result.success) {
            logOperationSuccess(
                "MouseController.move",
                `X=${x}, Y=${y}, RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "MouseController.move",
                result.errorMessage ?? "Failed to move mouse"
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async drag(
        startX: number,
        startY: number,
        endX: number,
        endY: number,
        button: MouseButton = MouseButton.LEFT
    ): Promise<BoolResult> {
        const buttonStr =
            typeof button === "string" ? button : (button as MouseButton);
        logOperationStart(
            "MouseController.drag",
            `FromX=${startX}, FromY=${startY}, ToX=${endX}, ToY=${endY}, Button=${buttonStr}`
        );
        const result = await this.callMcpTool("drag_mouse", {
            from_x: startX,
            from_y: startY,
            to_x: endX,
            to_y: endY,
            button: buttonStr,
        });
        if (result.success) {
            logOperationSuccess(
                "MouseController.drag",
                `RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "MouseController.drag",
                result.errorMessage ?? "Failed to drag mouse"
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async scroll(
        x: number,
        y: number,
        direction: ScrollDirection = ScrollDirection.UP,
        amount: number = 1
    ): Promise<BoolResult> {
        const directionStr =
            typeof direction === "string" ? direction : (direction as ScrollDirection);
        logOperationStart(
            "MouseController.scroll",
            `X=${x}, Y=${y}, Direction=${directionStr}, Amount=${amount}`
        );
        const result = await this.callMcpTool("scroll", {
            x,
            y,
            direction: directionStr,
            amount,
        });
        if (result.success) {
            logOperationSuccess(
                "MouseController.scroll",
                `RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "MouseController.scroll",
                result.errorMessage ?? "Failed to scroll"
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async getPosition(): Promise<CursorPosition> {
        const result = await this.callMcpTool("get_cursor_position", {});
        const requestId = result.requestId ?? "";
        if (!result.success) {
            return {
                requestId,
                success: false,
                errorMessage: result.errorMessage ?? "Failed to get cursor position",
                x: 0,
                y: 0,
            };
        }
        let x = 0;
        let y = 0;
        if (result.data != null) {
            try {
                const parsed =
                    typeof result.data === "string"
                        ? (JSON.parse(result.data) as { x?: number; y?: number })
                        : (result.data as { x?: number; y?: number });
                x = typeof parsed.x === "number" ? parsed.x : 0;
                y = typeof parsed.y === "number" ? parsed.y : 0;
            } catch {
                /* keep 0, 0 */
            }
        }
        return {
            requestId,
            success: true,
            x,
            y,
        };
    }
}

export class KeyboardController extends BaseService {
    async type(text: string): Promise<BoolResult> {
        logOperationStart("KeyboardController.type", `Text=${text}`);
        const result = await this.callMcpTool("input_text", { text });
        if (result.success) {
            logOperationSuccess(
                "KeyboardController.type",
                `TextLength=${text.length}, RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "KeyboardController.type",
                result.errorMessage ?? "Failed to type text"
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async press(keys: string | string[], hold = false): Promise<BoolResult> {
        const keyList = Array.isArray(keys) ? keys : [keys];
        logOperationStart("KeyboardController.press", `Keys=${keyList}, Hold=${hold}`);
        const result = await this.callMcpTool("press_keys", { keys: keyList, hold });
        if (result.success) {
            logOperationSuccess(
                "KeyboardController.press",
                `Keys=${keyList}, Hold=${hold}, RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "KeyboardController.press",
                result.errorMessage ?? "Failed to press keys"
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async release(keys: string | string[]): Promise<BoolResult> {
        const keyList = Array.isArray(keys) ? keys : [keys];
        const result = await this.callMcpTool("release_keys", { keys: keyList });
        return parseBoolResult(result, result.requestId ?? "");
    }
}

function parseWindowFromData(data: unknown): WindowInfo | undefined {
    if (data && typeof data === "object") {
        return data as WindowInfo;
    }
    if (typeof data === "string") {
        try {
            return JSON.parse(data) as WindowInfo;
        } catch {
            return undefined;
        }
    }
    return undefined;
}

export class WindowManager extends BaseService {
    async listRootWindows(timeoutMs = 3000): Promise<WindowListResult> {
        const result = await this.callMcpTool("list_root_windows", {
            timeout_ms: timeoutMs,
        });
        if (!result.success) {
            return {
                requestId: result.requestId ?? "",
                success: false,
                windows: [],
                errorMessage: result.errorMessage ?? "Failed to list root windows",
            };
        }
        let windows: WindowInfo[] = [];
        if (result.data) {
            try {
                const parsed =
                    typeof result.data === "string"
                        ? (JSON.parse(result.data) as unknown)
                        : result.data;
                if (Array.isArray(parsed)) {
                    windows = parsed.map((item) => parseWindowFromData(item) ?? ({} as WindowInfo));
                }
            } catch (e) {
                return {
                    requestId: result.requestId ?? "",
                    success: false,
                    windows: [],
                    errorMessage: `Failed to parse windows JSON: ${e}`,
                };
            }
        }
        return {
            requestId: result.requestId ?? "",
            success: true,
            windows,
        };
    }

    async getActiveWindow(): Promise<WindowInfoResult> {
        const result = await this.callMcpTool("get_active_window", {});
        if (!result.success) {
            return {
                requestId: result.requestId ?? "",
                success: false,
                window: undefined,
                errorMessage: result.errorMessage ?? "Failed to get active window",
            };
        }
        const window = parseWindowFromData(result.data);
        return {
            requestId: result.requestId ?? "",
            success: true,
            window,
        };
    }

    async activate(windowId: number): Promise<BoolResult> {
        logOperationStart("WindowManager.activate", `WindowId=${windowId}`);
        const result = await this.callMcpTool("activate_window", {
            window_id: windowId,
        });
        if (result.success) {
            logOperationSuccess(
                "WindowManager.activate",
                `WindowId=${windowId}, RequestId=${result.requestId ?? ""}`
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async close(windowId: number): Promise<BoolResult> {
        const result = await this.callMcpTool("close_window", {
            window_id: windowId,
        });
        return parseBoolResult(result, result.requestId ?? "");
    }

    async maximize(windowId: number): Promise<BoolResult> {
        const result = await this.callMcpTool("maximize_window", {
            window_id: windowId,
        });
        return parseBoolResult(result, result.requestId ?? "");
    }

    async minimize(windowId: number): Promise<BoolResult> {
        const result = await this.callMcpTool("minimize_window", {
            window_id: windowId,
        });
        return parseBoolResult(result, result.requestId ?? "");
    }

    async restore(windowId: number): Promise<BoolResult> {
        const result = await this.callMcpTool("restore_window", {
            window_id: windowId,
        });
        return parseBoolResult(result, result.requestId ?? "");
    }

    async resize(
        windowId: number,
        width: number,
        height: number
    ): Promise<BoolResult> {
        logOperationStart(
            "WindowManager.resize",
            `WindowId=${windowId}, Width=${width}, Height=${height}`
        );
        const result = await this.callMcpTool("resize_window", {
            window_id: windowId,
            width,
            height,
        });
        if (result.success) {
            logOperationSuccess(
                "WindowManager.resize",
                `RequestId=${result.requestId ?? ""}`
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async fullscreen(windowId: number): Promise<BoolResult> {
        logOperationStart("WindowManager.fullscreen", `WindowId=${windowId}`);
        const result = await this.callMcpTool("fullscreen_window", {
            window_id: windowId,
        });
        if (result.success) {
            logOperationSuccess(
                "WindowManager.fullscreen",
                `WindowId=${windowId}, RequestId=${result.requestId ?? ""}`
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }

    async focusMode(on: boolean): Promise<BoolResult> {
        logOperationStart("WindowManager.focusMode", `On=${on}`);
        const result = await this.callMcpTool("focus_mode", { on });
        if (result.success) {
            logOperationSuccess(
                "WindowManager.focusMode",
                `On=${on}, RequestId=${result.requestId ?? ""}`
            );
        }
        return parseBoolResult(result, result.requestId ?? "");
    }
}

function parseProcessFromData(data: unknown): ProcessInfo | undefined {
    if (data && typeof data === "object") {
        return data as ProcessInfo;
    }
    if (typeof data === "string") {
        try {
            return JSON.parse(data) as ProcessInfo;
        } catch {
            return undefined;
        }
    }
    return undefined;
}

function parseInstalledAppFromData(data: unknown): InstalledAppInfo | undefined {
    if (data && typeof data === "object") {
        return data as InstalledAppInfo;
    }
    if (typeof data === "string") {
        try {
            return JSON.parse(data) as InstalledAppInfo;
        } catch {
            return undefined;
        }
    }
    return undefined;
}

export class ApplicationManager extends BaseService {
    async start(
        command: string,
        workDirectory = "",
        activity = "",
    ): Promise<ProcessListResult> {
        let opDetails = `Command=${command}`;
        if (workDirectory) opDetails += `, WorkDirectory=${workDirectory}`;
        if (activity) opDetails += `, Activity=${activity}`;
        logOperationStart("ApplicationManager.start", opDetails);
        const args: Record<string, unknown> = { start_cmd: command };
        if (workDirectory) args.work_directory = workDirectory;
        if (activity) args.activity = activity;
        const result = await this.callMcpTool("start_app", args);
        if (!result.success) {
            logOperationError(
                "ApplicationManager.start",
                result.errorMessage ?? "Failed to start app"
            );
            return {
                requestId: result.requestId ?? "",
                success: false,
                data: [],
                errorMessage: result.errorMessage ?? "Failed to start app",
            };
        }
        let processes: ProcessInfo[] = [];
        if (result.data) {
            try {
                const parsed =
                    typeof result.data === "string"
                        ? (JSON.parse(result.data) as unknown)
                        : result.data;
                if (Array.isArray(parsed)) {
                    processes = parsed.map(
                        (item) => parseProcessFromData(item) ?? ({} as ProcessInfo)
                    );
                }
            } catch (e) {
                return {
                    requestId: result.requestId ?? "",
                    success: false,
                    data: [],
                    errorMessage: `Failed to parse processes JSON: ${e}`,
                };
            }
        }
        logOperationSuccess(
            "ApplicationManager.start",
            `Command=${command}, ProcessesCount=${processes.length}, RequestId=${result.requestId ?? ""}`
        );
        return {
            requestId: result.requestId ?? "",
            success: true,
            data: processes,
        };
    }

    async stopByPname(processName: string): Promise<AppOperationResult> {
        logOperationStart("ApplicationManager.stopByPname", `PName=${processName}`);
        const result = await this.callMcpTool("stop_app_by_pname", {
            pname: processName,
        });
        if (result.success) {
            logOperationSuccess(
                "ApplicationManager.stopByPname",
                `PName=${processName}, RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "ApplicationManager.stopByPname",
                result.errorMessage ?? "Failed to stop app by pname"
            );
        }
        return {
            requestId: result.requestId ?? "",
            success: result.success,
            errorMessage:
                result.errorMessage ??
                (result.success ? "" : "Failed to stop app by pname"),
        };
    }

    async stopByPid(pid: number): Promise<AppOperationResult> {
        logOperationStart("ApplicationManager.stopByPid", `PID=${pid}`);
        const result = await this.callMcpTool("stop_app_by_pid", { pid });
        if (result.success) {
            logOperationSuccess(
                "ApplicationManager.stopByPid",
                `PID=${pid}, RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "ApplicationManager.stopByPid",
                result.errorMessage ?? "Failed to stop app by pid"
            );
        }
        return {
            requestId: result.requestId ?? "",
            success: result.success,
            errorMessage:
                result.errorMessage ??
                (result.success ? "" : "Failed to stop app by pid"),
        };
    }

    async listInstalled(
        startMenu = true,
        desktop = false,
        ignoreSystemApps = true,
    ): Promise<InstalledAppListResult> {
        const result = await this.callMcpTool("get_installed_apps", {
            start_menu: startMenu,
            desktop,
            ignore_system_app: ignoreSystemApps,
        });
        if (!result.success) {
            return {
                requestId: result.requestId ?? "",
                success: false,
                data: [],
                errorMessage:
                    result.errorMessage ?? "Failed to get installed apps",
            };
        }
        let apps: InstalledAppInfo[] = [];
        if (result.data) {
            try {
                const parsed =
                    typeof result.data === "string"
                        ? (JSON.parse(result.data) as unknown)
                        : result.data;
                if (Array.isArray(parsed)) {
                    apps = parsed.map(
                        (item) => parseInstalledAppFromData(item) ?? ({} as InstalledAppInfo)
                    );
                }
            } catch (e) {
                return {
                    requestId: result.requestId ?? "",
                    success: false,
                    data: [],
                    errorMessage: `Failed to parse applications JSON: ${e}`,
                };
            }
        }
        return {
            requestId: result.requestId ?? "",
            success: true,
            data: apps,
        };
    }

    async stopByCmd(stopCmd: string): Promise<AppOperationResult> {
        logOperationStart("ApplicationManager.stopByCmd", `StopCmd=${stopCmd}`);
        const result = await this.callMcpTool("stop_app_by_cmd", {
            stop_cmd: stopCmd,
        });
        if (result.success) {
            logOperationSuccess(
                "ApplicationManager.stopByCmd",
                `StopCmd=${stopCmd}, RequestId=${result.requestId ?? ""}`
            );
        } else {
            logOperationError(
                "ApplicationManager.stopByCmd",
                result.errorMessage ?? "Failed to stop app by cmd"
            );
        }
        return {
            requestId: result.requestId ?? "",
            success: result.success,
            errorMessage:
                result.errorMessage ??
                (result.success ? "" : "Failed to stop app by cmd"),
        };
    }

    async getVisible(): Promise<ProcessListResult> {
        const result = await this.callMcpTool("list_visible_apps", {});
        if (!result.success) {
            return {
                requestId: result.requestId ?? "",
                success: false,
                data: [],
                errorMessage:
                    result.errorMessage ?? "Failed to list visible apps",
            };
        }
        let processes: ProcessInfo[] = [];
        if (result.data) {
            try {
                const parsed =
                    typeof result.data === "string"
                        ? (JSON.parse(result.data) as unknown)
                        : result.data;
                if (Array.isArray(parsed)) {
                    processes = parsed.map(
                        (item) => parseProcessFromData(item) ?? ({} as ProcessInfo)
                    );
                }
            } catch (e) {
                return {
                    requestId: result.requestId ?? "",
                    success: false,
                    data: [],
                    errorMessage: `Failed to parse visible apps JSON: ${e}`,
                };
            }
        }
        return {
            requestId: result.requestId ?? "",
            success: true,
            data: processes,
        };
    }
}

export class ScreenController extends BaseService {
    async capture(): Promise<OperationResult> {
        logOperationStart("ScreenController.capture", "");

        // Check if this environment supports direct screenshot
        const linkUrl = this.session.linkUrl ?? ""
        if (linkUrl) {
            const errorMsg =
                "This cloud environment does not support `screen.capture()`. " +
                "Please use `beta_take_screenshot()` instead.";
            logOperationError("ScreenController.capture", errorMsg);
            return {
                requestId: "",
                success: false,
                data: undefined,
                errorMessage: errorMsg,
            };
        }

        const result = await this.callMcpTool("system_screenshot", {});
        if (result.success) {
            logOperationSuccess(
                "ScreenController.capture",
                `RequestId=${result.requestId ?? ""}, ImageUrl=${result.data ?? "None"}`
            );
        } else {
            logOperationError(
                "ScreenController.capture",
                result.errorMessage ?? "Failed to take screenshot"
            );
        }
        return {
            requestId: result.requestId ?? "",
            success: result.success,
            data: result.data,
            errorMessage: result.errorMessage,
        };
    }

    async getSize(): Promise<ScreenSize> {
        logOperationStart("ScreenController.getSize", "");
        const result = await this.callMcpTool("get_screen_size", {});
        const requestId = result.requestId ?? "";
        if (!result.success) {
            logOperationError(
                "ScreenController.getSize",
                result.errorMessage ?? "Failed to get screen size"
            );
            return {
                requestId,
                success: false,
                errorMessage: result.errorMessage ?? "Failed to get screen size",
                width: 0,
                height: 0,
                dpiScalingFactor: 1.0,
            };
        }
        let width = 0;
        let height = 0;
        let dpiScalingFactor = 1.0;
        if (result.data != null) {
            try {
                const raw =
                    typeof result.data === "string"
                        ? (JSON.parse(result.data) as Record<string, unknown>)
                        : (result.data as Record<string, unknown>);
                width =
                    typeof raw.width === "number"
                        ? raw.width
                        : typeof raw.width === "string"
                            ? Number(raw.width) || 0
                            : 0;
                height =
                    typeof raw.height === "number"
                        ? raw.height
                        : typeof raw.height === "string"
                            ? Number(raw.height) || 0
                            : 0;
                const dpi =
                    raw.dpiScalingFactor ?? raw.dpi_scaling_factor;
                dpiScalingFactor =
                    typeof dpi === "number" && Number.isFinite(dpi) ? dpi : 1.0;
            } catch {
                /* keep defaults */
            }
        }
        logOperationSuccess(
            "ScreenController.getSize",
            `Width=${width}, Height=${height}, DpiScalingFactor=${dpiScalingFactor}, RequestId=${requestId}`
        );
        return {
            requestId,
            success: true,
            width,
            height,
            dpiScalingFactor,
        };
    }

    /**
     * Takes a screenshot of the Computer and returns raw binary image data.
     *
     * This API uses the MCP tool `screenshot` (wuying_capture) and returns raw
     * binary image data. The backend also returns the captured image dimensions
     * (width/height in pixels), which are exposed on `ScreenshotResult.width`
     * and `ScreenshotResult.height`. The backend metadata fields `type` and
     * `mime_type` are exposed on `ScreenshotResult.type` and `ScreenshotResult.mimeType`.
     *
     * @param format - The desired image format (default: "png"). Supported: "png", "jpeg", "jpg".
     * @returns ScreenshotResult containing the screenshot image data (Buffer) and metadata.
     * @throws ScreenError if screenshot fails or response cannot be decoded.
     * @throws Error if format is invalid.
     *
     * Note: This method only works in environments with linkUrl (e.g., Browser Use images).
     * For other environments, use `capture()` instead.
     */
    async betaTakeScreenshot(format: string = "png"): Promise<ScreenshotResult> {
        logOperationStart("ScreenController.betaTakeScreenshot", `format=${format}`);

        // Check if this environment supports betaTakeScreenshot
        const linkUrl = this.session.linkUrl ?? "";
        if (!linkUrl) {
            throw new ScreenError(
                "This cloud environment does not support `betaTakeScreenshot()`. " +
                "Please use `capture()` instead."
            );
        }

        // Validate format
        let fmt = (format || "").trim().toLowerCase();
        if (fmt === "jpg") {
            fmt = "jpeg";
        }
        if (fmt !== "png" && fmt !== "jpeg") {
            throw new Error("Invalid format: must be 'png', 'jpeg', or 'jpg'");
        }

        // Call MCP tool
        const args = { format: fmt };
        const result = await this.callMcpTool("screenshot", args);

        if (!result.success) {
            const errorMsg = `Failed to take screenshot via MCP tool 'screenshot': ${result.errorMessage}`;
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        if (typeof result.data !== "string" || !result.data.trim()) {
            const errorMsg = "Screenshot tool returned empty data";
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        const text = result.data.trim();

        // Backend contract: screenshot tool returns a JSON object string with
        // top-level field "data" containing base64.
        if (!text.startsWith("{")) {
            const errorMsg = "Screenshot tool returned non-JSON data";
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        let obj: Record<string, unknown>;
        try {
            obj = JSON.parse(text) as Record<string, unknown>;
        } catch (e) {
            const errorMsg = `Invalid screenshot JSON: ${e}`;
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        if (typeof obj !== "object" || obj === null) {
            const errorMsg = "Invalid screenshot JSON: expected object";
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        const shotType = obj.type as string | undefined;
        const mimeType = obj.mime_type as string | undefined;
        const b64 = obj.data as string | undefined;

        if (typeof b64 !== "string" || !b64.trim()) {
            const errorMsg = "Screenshot JSON missing base64 field";
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        if (typeof shotType !== "string" || !shotType.trim()) {
            const errorMsg = "Invalid screenshot JSON: expected non-empty string 'type'";
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        if (typeof mimeType !== "string" || !mimeType.trim()) {
            const errorMsg = "Invalid screenshot JSON: expected non-empty string 'mime_type'";
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        const width = obj.width as number | undefined;
        const height = obj.height as number | undefined;

        if (width !== undefined && typeof width !== "number") {
            const errorMsg = "Invalid screenshot JSON: expected integer 'width'";
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        if (height !== undefined && typeof height !== "number") {
            const errorMsg = "Invalid screenshot JSON: expected integer 'height'";
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        // Decode base64 data
        let raw: Buffer;
        try {
            raw = Buffer.from(b64, "base64");
        } catch (e) {
            const errorMsg = `Failed to decode screenshot data: ${e}`;
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        // Verify magic bytes
        const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
        const jpegMagic = Buffer.from([0xff, 0xd8, 0xff]);
        const expectedMagic = fmt === "jpeg" ? jpegMagic : pngMagic;

        if (!raw.subarray(0, expectedMagic.length).equals(expectedMagic)) {
            const errorMsg = `Screenshot data does not match expected format '${fmt}'`;
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        // Verify MIME type
        const expectedMimeType = fmt === "png" ? "image/png" : "image/jpeg";
        if (mimeType.trim().toLowerCase() !== expectedMimeType) {
            const errorMsg = `Screenshot JSON mime_type does not match expected format: expected '${expectedMimeType}', got '${mimeType}'`;
            logOperationError("ScreenController.betaTakeScreenshot", errorMsg);
            throw new ScreenError(errorMsg);
        }

        logOperationSuccess(
            "ScreenController.betaTakeScreenshot",
            `RequestId=${result.requestId ?? ""}, Size=${raw.length} bytes, Dimensions=${width}x${height}, Format=${fmt}`
        );

        return {
            requestId: result.requestId ?? "",
            success: true,
            errorMessage: "",
            type: shotType,
            data: raw,
            mimeType: mimeType,
            width: width,
            height: height,
        };
    }
}

/**
 * Computer module for desktop automation. Use sub-modules: mouse, keyboard, window, app, screen.
 */
export class Computer {
    /** Mouse operations (click, move, drag, scroll). */
    mouse: MouseController;
    /** Keyboard input (type, press keys). */
    keyboard: KeyboardController;
    window: WindowManager;
    app: ApplicationManager;
    screen: ScreenController;

    constructor(session: SessionLike) {
        this.mouse = new MouseController(session);
        this.keyboard = new KeyboardController(session);
        this.window = new WindowManager(session);
        this.app = new ApplicationManager(session);
        this.screen = new ScreenController(session);
    }

    toJSON(): Record<string, unknown> {
        return { type: "Computer" };
    }

    /** @deprecated Use computer.screen.capture() instead */
    async screenshot(): Promise<OperationResult> {
        return this.screen.capture();
    }

    /** @deprecated Use computer.mouse.click() instead */
    async mouseClick(
        x: number,
        y: number,
        button?: MouseButton
    ): Promise<BoolResult> {
        return this.mouse.click(x, y, button ?? MouseButton.LEFT);
    }

    /** @deprecated Use computer.keyboard.press() instead */
    async keyPress(key: string): Promise<BoolResult> {
        return this.keyboard.press(key);
    }
}
