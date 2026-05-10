import { expect, test } from "vitest";

import { initials } from "./lib";

test("converts name to initials", () => {
  expect(initials("Peter\t\n\r\v Parker")).toBe("PP");
  expect(initials("Peter")).toBe("PE");
  expect(initials("")).toBe("");
});
