import { expect, test } from "vitest";

import { human } from "./lib";

test("converts duration to human form", () => {
  expect(human(1)).toBe("1ms");
  expect(human(100)).toBe("100ms");
  expect(human(1000)).toBe("1s");
  expect(human(10 * 1000 + 500)).toBe("11s");
  expect(human(60 * 1000)).toBe("1m");
  expect(human(140 * 1000)).toBe("2m20s");
  expect(human(60 * 60 * 1000)).toBe("1h");
  expect(human(140 * 60 * 1000)).toBe("2h20m");
});
