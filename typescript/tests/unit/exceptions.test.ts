import {
    AGBError,
    AuthenticationError,
    APIError,
    FileError,
    CommandError,
    SessionError,
    BrowserError,
    ApplicationError,
    ClearanceTimeoutError,
} from "../../src/exceptions";

describe("Exceptions", () => {
    test("AGBError is an instance of Error", () => {
        const err = new AGBError("test error");
        expect(err).toBeInstanceOf(Error);
        expect(err).toBeInstanceOf(AGBError);
        expect(err.message).toBe("test error");
        expect(err.name).toBe("AGBError");
    });

    test("AGBError accepts extra", () => {
        const err = new AGBError("msg", { code: "E1" });
        expect(err.extra).toEqual({ code: "E1" });
    });

    test("AuthenticationError extends AGBError", () => {
        const err = new AuthenticationError("auth failed");
        expect(err).toBeInstanceOf(AGBError);
        expect(err.name).toBe("AuthenticationError");
    });

    test("APIError includes statusCode", () => {
        const err = new APIError("api error", 404);
        expect(err).toBeInstanceOf(AGBError);
        expect(err.statusCode).toBe(404);
    });

    test("FileError extends AGBError", () => {
        const err = new FileError("file error");
        expect(err).toBeInstanceOf(AGBError);
        expect(err.name).toBe("FileError");
    });

    test("CommandError extends AGBError", () => {
        const err = new CommandError("cmd error");
        expect(err).toBeInstanceOf(AGBError);
    });

    test("SessionError extends AGBError", () => {
        const err = new SessionError("session error");
        expect(err).toBeInstanceOf(AGBError);
    });

    test("BrowserError extends AGBError", () => {
        const err = new BrowserError("browser error");
        expect(err).toBeInstanceOf(AGBError);
    });

    test("ApplicationError extends AGBError", () => {
        const err = new ApplicationError("app error");
        expect(err).toBeInstanceOf(AGBError);
        expect(err.name).toBe("ApplicationError");
    });

    test("ClearanceTimeoutError extends AGBError", () => {
        const err = new ClearanceTimeoutError("timeout");
        expect(err).toBeInstanceOf(AGBError);
        expect(err.name).toBe("ClearanceTimeoutError");
    });
});
