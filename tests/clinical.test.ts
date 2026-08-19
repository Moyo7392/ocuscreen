import { describe, expect, it } from "vitest";
import { recommendationFor } from "@/lib/clinical";

describe("referral policy", () => {
  it("keeps grades 0–1 in routine rescreening", () => { expect(recommendationFor(0)).toMatch(/Routine/); expect(recommendationFor(1)).toMatch(/Routine/); });
  it("advises referral for grades 2–4", () => { for (const grade of [2,3,4] as const) expect(recommendationFor(grade)).toMatch(/ophthalmologist/); });
});
