import { describe, expect, it } from "vitest";
import { DISCLAIMER, GRADE_LABELS, recommendationFor, toneFor } from "@/lib/clinical";

describe("referral policy", () => {
  it("keeps grades 0–1 in routine rescreening", () => {
    expect(recommendationFor(0)).toMatch(/Routine/);
    expect(recommendationFor(1)).toMatch(/Routine/);
  });

  it("advises referral for grades 2–4", () => {
    for (const grade of [2, 3, 4] as const) {
      expect(recommendationFor(grade)).toMatch(/ophthalmologist/);
    }
  });

  it("maps all five supported grades to distinct labels", () => {
    expect(Object.keys(GRADE_LABELS)).toEqual(["0", "1", "2", "3", "4"]);
    expect(new Set(Object.values(GRADE_LABELS)).size).toBe(5);
  });

  it("escalates the visual tone as severity increases", () => {
    expect(toneFor(0)).toBe("safe");
    expect(toneFor(1)).toBe("safe");
    expect(toneFor(2)).toBe("warning");
    expect(toneFor(3)).toBe("danger");
    expect(toneFor(4)).toBe("danger");
  });

  it("states that the product is not a diagnostic device", () => {
    expect(DISCLAIMER).toMatch(/not an FDA-cleared diagnostic device/i);
    expect(DISCLAIMER).toMatch(/does not replace examination/i);
  });
});
