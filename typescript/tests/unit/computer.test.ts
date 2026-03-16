import { BaseService } from "../../src/api/base-service";
import type { SessionLike } from "../../src/api/base-service";
import {
    MouseController,
    KeyboardController,
    WindowManager,
    ApplicationManager,
    ScreenController,
    Computer,
    MouseButton,
    ScrollDirection,
} from "../../src/modules/computer/computer";

const mockSession: SessionLike = {
    getApiKey: () => "test-key",
    getSessionId: () => "test-session",
    getClient: () => ({}),
};

describe("MouseController", () => {
    let mouse: MouseController;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        mouse = new MouseController(mockSession);
        spy = jest.spyOn(mouse as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("click default left button", async () => {
        spy.mockResolvedValue({ requestId: "req-1", success: true, data: "true" });
        const r = await mouse.click(100, 200);
        expect(r.success).toBe(true);
        expect(r.data).toBe(true);
        expect(r.requestId).toBe("req-1");
        expect(spy).toHaveBeenCalledWith("click_mouse", { x: 100, y: 200, button: "left" });
    });

    test("click right button", async () => {
        spy.mockResolvedValue({ requestId: "req-2", success: true, data: "true" });
        const r = await mouse.click(50, 60, MouseButton.RIGHT);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("click_mouse", { x: 50, y: 60, button: "right" });
    });

    test("click middle button", async () => {
        spy.mockResolvedValue({ requestId: "req-3", success: true, data: "true" });
        await mouse.click(10, 20, MouseButton.MIDDLE);
        expect(spy).toHaveBeenCalledWith("click_mouse", { x: 10, y: 20, button: "middle" });
    });

    test("click double left button", async () => {
        spy.mockResolvedValue({ requestId: "req-dl", success: true, data: "true" });
        await mouse.click(5, 5, MouseButton.DOUBLE_LEFT);
        expect(spy).toHaveBeenCalledWith("click_mouse", { x: 5, y: 5, button: "double_left" });
    });

    test("click failure", async () => {
        spy.mockResolvedValue({ requestId: "req-f", success: false, errorMessage: "Click failed" });
        const r = await mouse.click(0, 0);
        expect(r.success).toBe(false);
        expect(r.data).toBe(false);
        expect(r.errorMessage).toBe("Click failed");
    });

    test("move", async () => {
        spy.mockResolvedValue({ requestId: "req-m", success: true, data: "true" });
        const r = await mouse.move(300, 400);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("move_mouse", { x: 300, y: 400 });
    });

    test("move failure", async () => {
        spy.mockResolvedValue({ requestId: "req-mf", success: false, errorMessage: "Move failed" });
        const r = await mouse.move(0, 0);
        expect(r.success).toBe(false);
        expect(r.errorMessage).toBe("Move failed");
    });

    test("drag", async () => {
        spy.mockResolvedValue({ requestId: "req-d", success: true, data: "true" });
        const r = await mouse.drag(10, 20, 100, 200);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("drag_mouse", {
            from_x: 10, from_y: 20, to_x: 100, to_y: 200, button: "left",
        });
    });

    test("drag with button", async () => {
        spy.mockResolvedValue({ requestId: "req-db", success: true, data: "true" });
        const r = await mouse.drag(0, 0, 50, 50, MouseButton.RIGHT);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("drag_mouse", {
            from_x: 0, from_y: 0, to_x: 50, to_y: 50, button: "right",
        });
    });

    test("drag failure", async () => {
        spy.mockResolvedValue({ requestId: "req-df", success: false, errorMessage: "Drag error" });
        const r = await mouse.drag(0, 0, 1, 1);
        expect(r.success).toBe(false);
        expect(r.errorMessage).toBe("Drag error");
    });

    test("scroll with coordinates and direction", async () => {
        spy.mockResolvedValue({ requestId: "req-s", success: true, data: "true" });
        const r = await mouse.scroll(400, 300, ScrollDirection.DOWN, 3);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("scroll", {
            x: 400, y: 300, direction: "down", amount: 3,
        });
    });

    test("scroll default direction and amount", async () => {
        spy.mockResolvedValue({ requestId: "req-s2", success: true, data: "true" });
        await mouse.scroll(0, 0);
        expect(spy).toHaveBeenCalledWith("scroll", {
            x: 0, y: 0, direction: "up", amount: 1,
        });
    });

    test("scroll left/right", async () => {
        spy.mockResolvedValue({ requestId: "req-s3", success: true, data: "true" });
        await mouse.scroll(100, 100, ScrollDirection.LEFT, 5);
        expect(spy).toHaveBeenCalledWith("scroll", {
            x: 100, y: 100, direction: "left", amount: 5,
        });
    });

    test("scroll failure", async () => {
        spy.mockResolvedValue({ requestId: "req-sf", success: false, errorMessage: "Scroll error" });
        const r = await mouse.scroll(0, 0, ScrollDirection.UP);
        expect(r.success).toBe(false);
    });

    test("getPosition", async () => {
        spy.mockResolvedValue({
            requestId: "req-p", success: true,
            data: { x: 512, y: 384 },
        });
        const r = await mouse.getPosition();
        expect(r.success).toBe(true);
        expect(r.x).toBe(512);
        expect(r.y).toBe(384);
        expect(spy).toHaveBeenCalledWith("get_cursor_position", {});
    });

    test("getPosition failure", async () => {
        spy.mockResolvedValue({ requestId: "req-pf", success: false, errorMessage: "No position" });
        const r = await mouse.getPosition();
        expect(r.success).toBe(false);
        expect(r.x).toBe(0);
        expect(r.y).toBe(0);
    });
});

describe("KeyboardController", () => {
    let keyboard: KeyboardController;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        keyboard = new KeyboardController(mockSession);
        spy = jest.spyOn(keyboard as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("type text", async () => {
        spy.mockResolvedValue({ requestId: "req-t", success: true, data: "true" });
        const r = await keyboard.type("hello world");
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("input_text", { text: "hello world" });
    });

    test("type failure", async () => {
        spy.mockResolvedValue({ requestId: "req-tf", success: false, errorMessage: "Type failed" });
        const r = await keyboard.type("abc");
        expect(r.success).toBe(false);
        expect(r.errorMessage).toBe("Type failed");
    });

    test("press single key string", async () => {
        spy.mockResolvedValue({ requestId: "req-k", success: true, data: "true" });
        const r = await keyboard.press("Enter");
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("press_keys", { keys: ["Enter"], hold: false });
    });

    test("press multiple keys array", async () => {
        spy.mockResolvedValue({ requestId: "req-k2", success: true, data: "true" });
        const r = await keyboard.press(["ctrl", "c"]);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("press_keys", { keys: ["ctrl", "c"], hold: false });
    });

    test("press with hold=true", async () => {
        spy.mockResolvedValue({ requestId: "req-k3", success: true, data: "true" });
        await keyboard.press("Shift", true);
        expect(spy).toHaveBeenCalledWith("press_keys", { keys: ["Shift"], hold: true });
    });

    test("press failure", async () => {
        spy.mockResolvedValue({ requestId: "req-kf", success: false, errorMessage: "Key error" });
        const r = await keyboard.press("F13");
        expect(r.success).toBe(false);
    });

    test("release single key", async () => {
        spy.mockResolvedValue({ requestId: "req-r", success: true, data: "true" });
        const r = await keyboard.release("Shift");
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("release_keys", { keys: ["Shift"] });
    });

    test("release multiple keys", async () => {
        spy.mockResolvedValue({ requestId: "req-r2", success: true, data: "true" });
        const r = await keyboard.release(["ctrl", "alt"]);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("release_keys", { keys: ["ctrl", "alt"] });
    });
});

describe("WindowManager", () => {
    let wm: WindowManager;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        wm = new WindowManager(mockSession);
        spy = jest.spyOn(wm as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("listRootWindows success", async () => {
        const windows = [
            { id: "w1", title: "Window 1" },
            { id: "w2", title: "Window 2" },
        ];
        spy.mockResolvedValue({
            requestId: "req-lw", success: true,
            data: JSON.stringify(windows),
        });
        const r = await wm.listRootWindows();
        expect(r.success).toBe(true);
        expect(r.windows).toHaveLength(2);
        expect(r.windows[0].id).toBe("w1");
    });

    test("listRootWindows failure", async () => {
        spy.mockResolvedValue({ requestId: "req-lwf", success: false, errorMessage: "List error" });
        const r = await wm.listRootWindows();
        expect(r.success).toBe(false);
        expect(r.windows).toEqual([]);
    });

    test("listRootWindows parse error", async () => {
        spy.mockResolvedValue({ requestId: "req-lwe", success: true, data: "not json" });
        const r = await wm.listRootWindows();
        expect(r.success).toBe(false);
        expect(r.errorMessage).toContain("Failed to parse windows JSON");
    });

    test("listRootWindows with object data", async () => {
        const windows = [{ id: "w1", title: "Test" }];
        spy.mockResolvedValue({ requestId: "req-lwo", success: true, data: windows });
        const r = await wm.listRootWindows();
        expect(r.success).toBe(true);
        expect(r.windows).toHaveLength(1);
    });

    test("listRootWindows with timeoutMs parameter", async () => {
        spy.mockResolvedValue({
            requestId: "req-lwt", success: true,
            data: JSON.stringify([]),
        });
        await wm.listRootWindows(5000);
        expect(spy).toHaveBeenCalledWith("list_root_windows", { timeout_ms: 5000 });
    });

    test("getActiveWindow success", async () => {
        spy.mockResolvedValue({
            requestId: "req-aw", success: true,
            data: JSON.stringify({ id: "active-1", title: "Active" }),
        });
        const r = await wm.getActiveWindow();
        expect(r.success).toBe(true);
        expect(r.window?.id).toBe("active-1");
    });

    test("getActiveWindow failure", async () => {
        spy.mockResolvedValue({ requestId: "req-awf", success: false, errorMessage: "No window" });
        const r = await wm.getActiveWindow();
        expect(r.success).toBe(false);
        expect(r.window).toBeUndefined();
    });

    test("getActiveWindow with object data", async () => {
        spy.mockResolvedValue({
            requestId: "req-awo", success: true,
            data: { id: "win-obj", title: "Object Window" },
        });
        const r = await wm.getActiveWindow();
        expect(r.success).toBe(true);
        expect(r.window?.id).toBe("win-obj");
    });

    test("activate", async () => {
        spy.mockResolvedValue({ requestId: "req-a", success: true, data: "true" });
        const r = await wm.activate(1);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("activate_window", { window_id: 1 });
    });

    test("close", async () => {
        spy.mockResolvedValue({ requestId: "req-c", success: true, data: "true" });
        const r = await wm.close(1);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("close_window", { window_id: 1 });
    });

    test("maximize", async () => {
        spy.mockResolvedValue({ requestId: "req-mx", success: true, data: "true" });
        const r = await wm.maximize(1);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("maximize_window", { window_id: 1 });
    });

    test("minimize", async () => {
        spy.mockResolvedValue({ requestId: "req-mn", success: true, data: "true" });
        const r = await wm.minimize(1);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("minimize_window", { window_id: 1 });
    });

    test("restore", async () => {
        spy.mockResolvedValue({ requestId: "req-rs", success: true, data: "true" });
        const r = await wm.restore(1);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("restore_window", { window_id: 1 });
    });

    test("resize", async () => {
        spy.mockResolvedValue({ requestId: "req-rz", success: true, data: "true" });
        const r = await wm.resize(1, 800, 600);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("resize_window", {
            window_id: 1, width: 800, height: 600,
        });
    });

    test("fullscreen", async () => {
        spy.mockResolvedValue({ requestId: "req-fs", success: true, data: "true" });
        const r = await wm.fullscreen(1);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("fullscreen_window", { window_id: 1 });
    });

    test("focusMode on", async () => {
        spy.mockResolvedValue({ requestId: "req-fm", success: true, data: "true" });
        const r = await wm.focusMode(true);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("focus_mode", { on: true });
    });

    test("focusMode off", async () => {
        spy.mockResolvedValue({ requestId: "req-fmo", success: true, data: "true" });
        const r = await wm.focusMode(false);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("focus_mode", { on: false });
    });
});

describe("ApplicationManager", () => {
    let app: ApplicationManager;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        app = new ApplicationManager(mockSession);
        spy = jest.spyOn(app as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("start with command only", async () => {
        const procs = [{ pid: 123, name: "myapp" }];
        spy.mockResolvedValue({
            requestId: "req-sa", success: true,
            data: JSON.stringify(procs),
        });
        const r = await app.start("myapp");
        expect(r.success).toBe(true);
        expect(r.data).toHaveLength(1);
        expect(r.data[0].pid).toBe(123);
        expect(spy).toHaveBeenCalledWith("start_app", { start_cmd: "myapp" });
    });

    test("start with workDirectory and activity", async () => {
        spy.mockResolvedValue({
            requestId: "req-sa2", success: true,
            data: JSON.stringify([{ pid: 456, name: "chrome" }]),
        });
        await app.start("chrome", "/home/user", "main");
        expect(spy).toHaveBeenCalledWith("start_app", {
            start_cmd: "chrome",
            work_directory: "/home/user",
            activity: "main",
        });
    });

    test("start failure", async () => {
        spy.mockResolvedValue({ requestId: "req-saf", success: false, errorMessage: "Start failed" });
        const r = await app.start("bad-app");
        expect(r.success).toBe(false);
        expect(r.data).toEqual([]);
    });

    test("start parse error", async () => {
        spy.mockResolvedValue({ requestId: "req-sae", success: true, data: "not-json" });
        const r = await app.start("app");
        expect(r.success).toBe(false);
        expect(r.errorMessage).toContain("Failed to parse processes JSON");
    });

    test("stopByPname", async () => {
        spy.mockResolvedValue({ requestId: "req-sp", success: true, data: "true" });
        const r = await app.stopByPname("myapp");
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("stop_app_by_pname", { pname: "myapp" });
    });

    test("stopByPname failure", async () => {
        spy.mockResolvedValue({ requestId: "req-spf", success: false, errorMessage: "Not found" });
        const r = await app.stopByPname("unknown");
        expect(r.success).toBe(false);
    });

    test("stopByPid", async () => {
        spy.mockResolvedValue({ requestId: "req-pid", success: true, data: "true" });
        const r = await app.stopByPid(12345);
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("stop_app_by_pid", { pid: 12345 });
    });

    test("stopByPid failure", async () => {
        spy.mockResolvedValue({ requestId: "req-pidf", success: false, errorMessage: "No process" });
        const r = await app.stopByPid(99999);
        expect(r.success).toBe(false);
    });

    test("stopByCmd", async () => {
        spy.mockResolvedValue({ requestId: "req-sc", success: true, data: "true" });
        const r = await app.stopByCmd("kill myapp");
        expect(r.success).toBe(true);
        expect(spy).toHaveBeenCalledWith("stop_app_by_cmd", { stop_cmd: "kill myapp" });
    });

    test("stopByCmd failure", async () => {
        spy.mockResolvedValue({ requestId: "req-scf", success: false, errorMessage: "Cmd failed" });
        const r = await app.stopByCmd("bad-cmd");
        expect(r.success).toBe(false);
    });

    test("getVisible success", async () => {
        const procs = [{ pid: 111, name: "visible-app" }];
        spy.mockResolvedValue({
            requestId: "req-gv", success: true,
            data: JSON.stringify(procs),
        });
        const r = await app.getVisible();
        expect(r.success).toBe(true);
        expect(r.data).toHaveLength(1);
    });

    test("getVisible failure", async () => {
        spy.mockResolvedValue({ requestId: "req-gvf", success: false, errorMessage: "Error" });
        const r = await app.getVisible();
        expect(r.success).toBe(false);
        expect(r.data).toEqual([]);
    });

    test("getVisible parse error", async () => {
        spy.mockResolvedValue({ requestId: "req-gve", success: true, data: "{bad" });
        const r = await app.getVisible();
        expect(r.success).toBe(false);
        expect(r.errorMessage).toContain("Failed to parse visible apps JSON");
    });

    test("listInstalled default params", async () => {
        const apps = [{ name: "App1", path: "/usr/bin/app1" }];
        spy.mockResolvedValue({
            requestId: "req-li", success: true,
            data: JSON.stringify(apps),
        });
        const r = await app.listInstalled();
        expect(r.success).toBe(true);
        expect(r.data).toHaveLength(1);
        expect(spy).toHaveBeenCalledWith("get_installed_apps", {
            start_menu: true,
            desktop: false,
            ignore_system_app: true,
        });
    });

    test("listInstalled custom params", async () => {
        spy.mockResolvedValue({
            requestId: "req-li2", success: true,
            data: JSON.stringify([]),
        });
        await app.listInstalled(false, true, false);
        expect(spy).toHaveBeenCalledWith("get_installed_apps", {
            start_menu: false,
            desktop: true,
            ignore_system_app: false,
        });
    });

    test("listInstalled failure", async () => {
        spy.mockResolvedValue({ requestId: "req-lif", success: false, errorMessage: "List error" });
        const r = await app.listInstalled();
        expect(r.success).toBe(false);
        expect(r.data).toEqual([]);
    });

    test("listInstalled parse error", async () => {
        spy.mockResolvedValue({ requestId: "req-lie", success: true, data: "bad-json" });
        const r = await app.listInstalled();
        expect(r.success).toBe(false);
        expect(r.errorMessage).toContain("Failed to parse applications JSON");
    });
});

describe("ScreenController", () => {
    let screen: ScreenController;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        screen = new ScreenController(mockSession);
        spy = jest.spyOn(screen as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("capture success", async () => {
        spy.mockResolvedValue({
            requestId: "req-sc", success: true,
            data: "data:image/png;base64,...",
        });
        const r = await screen.capture();
        expect(r.success).toBe(true);
        expect(r.data).toContain("data:image/png");
    });

    test("capture failure", async () => {
        spy.mockResolvedValue({
            requestId: "req-scf", success: false,
            errorMessage: "Screenshot failed",
        });
        const r = await screen.capture();
        expect(r.success).toBe(false);
        expect(r.errorMessage).toBe("Screenshot failed");
    });

    test("getSize success with string data", async () => {
        spy.mockResolvedValue({
            requestId: "req-gs", success: true,
            data: JSON.stringify({ width: 1920, height: 1080 }),
        });
        const r = await screen.getSize();
        expect(r.success).toBe(true);
        expect(r.width).toBe(1920);
        expect(r.height).toBe(1080);
        expect(r.dpiScalingFactor).toBe(1.0);
    });

    test("getSize success with object data", async () => {
        spy.mockResolvedValue({
            requestId: "req-gs2", success: true,
            data: { width: 1024, height: 768, dpiScalingFactor: 1.5 },
        });
        const r = await screen.getSize();
        expect(r.success).toBe(true);
        expect(r.width).toBe(1024);
        expect(r.height).toBe(768);
        expect(r.dpiScalingFactor).toBe(1.5);
    });

    test("getSize failure", async () => {
        spy.mockResolvedValue({
            requestId: "req-gsf", success: false,
            errorMessage: "Size error",
        });
        const r = await screen.getSize();
        expect(r.success).toBe(false);
        expect(r.width).toBe(0);
        expect(r.height).toBe(0);
        expect(r.dpiScalingFactor).toBe(1.0);
    });

    test("getSize with unparseable string", async () => {
        spy.mockResolvedValue({
            requestId: "req-gsu", success: true,
            data: "not-json",
        });
        const r = await screen.getSize();
        expect(r.success).toBe(true);
        expect(r.width).toBe(0);
        expect(r.height).toBe(0);
        expect(r.dpiScalingFactor).toBe(1.0);
    });
});

describe("Computer", () => {
    let computer: Computer;

    beforeEach(() => {
        computer = new Computer(mockSession);
    });

    test("has all sub-controllers", () => {
        expect(computer.mouse).toBeInstanceOf(MouseController);
        expect(computer.keyboard).toBeInstanceOf(KeyboardController);
        expect(computer.window).toBeInstanceOf(WindowManager);
        expect(computer.app).toBeInstanceOf(ApplicationManager);
        expect(computer.screen).toBeInstanceOf(ScreenController);
    });

    test("toJSON returns type Computer", () => {
        expect(computer.toJSON()).toEqual({ type: "Computer" });
    });

    test("deprecated screenshot delegates to screen.capture", async () => {
        const captureSpy = jest.spyOn(computer.screen, "capture").mockResolvedValue({
            requestId: "req-1", success: true, data: "img",
        });
        const r = await computer.screenshot();
        expect(r.success).toBe(true);
        expect(captureSpy).toHaveBeenCalled();
        captureSpy.mockRestore();
    });

    test("deprecated mouseClick delegates to mouse.click", async () => {
        const clickSpy = jest.spyOn(computer.mouse, "click").mockResolvedValue({
            requestId: "req-1", success: true, data: true,
        });
        const r = await computer.mouseClick(100, 200, MouseButton.RIGHT);
        expect(r.success).toBe(true);
        expect(clickSpy).toHaveBeenCalledWith(100, 200, MouseButton.RIGHT);
        clickSpy.mockRestore();
    });

    test("deprecated mouseClick defaults to LEFT", async () => {
        const clickSpy = jest.spyOn(computer.mouse, "click").mockResolvedValue({
            requestId: "req-1", success: true, data: true,
        });
        await computer.mouseClick(10, 20);
        expect(clickSpy).toHaveBeenCalledWith(10, 20, MouseButton.LEFT);
        clickSpy.mockRestore();
    });

    test("deprecated keyPress delegates to keyboard.press", async () => {
        const pressSpy = jest.spyOn(computer.keyboard, "press").mockResolvedValue({
            requestId: "req-1", success: true, data: true,
        });
        const r = await computer.keyPress("Enter");
        expect(r.success).toBe(true);
        expect(pressSpy).toHaveBeenCalledWith("Enter");
        pressSpy.mockRestore();
    });
});

describe("parseBoolResult edge cases", () => {
    let mouse: MouseController;
    let spy: jest.SpyInstance;

    beforeEach(() => {
        mouse = new MouseController(mockSession);
        spy = jest.spyOn(mouse as any, "callMcpTool");
    });
    afterEach(() => spy.mockRestore());

    test("data=true (boolean)", async () => {
        spy.mockResolvedValue({ requestId: "r", success: true, data: true });
        const r = await mouse.move(1, 1);
        expect(r.data).toBe(true);
    });

    test("data='True' (uppercase)", async () => {
        spy.mockResolvedValue({ requestId: "r", success: true, data: "True" });
        const r = await mouse.move(1, 1);
        expect(r.data).toBe(true);
    });

    test("data='false'", async () => {
        spy.mockResolvedValue({ requestId: "r", success: true, data: "false" });
        const r = await mouse.move(1, 1);
        expect(r.data).toBe(false);
    });

    test("data=null on failure returns false", async () => {
        spy.mockResolvedValue({ requestId: "r", success: false, data: null, errorMessage: "err" });
        const r = await mouse.move(1, 1);
        expect(r.data).toBe(false);
    });

    test("missing requestId defaults to empty string", async () => {
        spy.mockResolvedValue({ success: true, data: "true" });
        const r = await mouse.move(1, 1);
        expect(r.requestId).toBe("");
    });
});
