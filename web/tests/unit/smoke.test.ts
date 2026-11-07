import { describe, expect, it } from "vitest";

describe("app bootstrap", () => {
  it("renders the app heading into #app", async () => {
    document.body.innerHTML = '<div id="app"></div>';
    await import("../../src/main");
    expect(document.querySelector("h1")?.textContent).toBe("FEM1D Studio");
  });
});
