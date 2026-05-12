import { expect, test } from "vitest";

import { applyJsonMergePatch, computeJsonMergePatch } from "./jsonMergePatch";

test("applies json merge patch", () => {
  expect(applyJsonMergePatch({}, null)).toStrictEqual(null);
  expect(applyJsonMergePatch({}, {})).toStrictEqual({});
  expect(
    applyJsonMergePatch({ x: 1, y: 2, z: 3 }, { x: null, z: { t: 5 } }),
  ).toStrictEqual({ y: 2, z: { t: 5 } });
});

test("computes json merge patch", () => {
  expect(computeJsonMergePatch({ z: 3 }, { x: 1, y: 2 })).toStrictEqual({
    z: null,
    x: 1,
    y: 2,
  });
});
