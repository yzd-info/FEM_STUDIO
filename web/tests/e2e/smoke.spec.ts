import { expect, test } from "@playwright/test";

test("boş sayfa açılır ve başlık görünür", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle("FEM1D Studio");
  await expect(page.locator("h1")).toHaveText("FEM1D Studio");
});
