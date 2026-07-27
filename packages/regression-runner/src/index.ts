export function stableJson(value: unknown, space = 2): string {
  return JSON.stringify(sortValue(value), null, space);
}

export function compactStableJson(value: unknown): string {
  return JSON.stringify(sortValue(value));
}

export function sortValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, item]) => [key, sortValue(item)])
    );
  }
  return value;
}

export function compareSubset(
  failures: string[],
  label: string,
  expected: unknown,
  actual: unknown
): void {
  if (Array.isArray(expected)) {
    compareJson(failures, label, expected, actual);
    return;
  }
  if (expected && typeof expected === "object") {
    for (const [key, value] of Object.entries(expected)) {
      compareSubset(
        failures,
        `${label}.${key}`,
        value,
        (actual as Record<string, unknown> | undefined)?.[key]
      );
    }
    return;
  }
  comparePrimitive(failures, label, expected, actual);
}

export function compareJson(
  failures: string[],
  label: string,
  expected: unknown,
  actual: unknown
): void {
  const expectedText = stableJson(expected);
  const actualText = stableJson(actual);
  if (expectedText !== actualText) {
    failures.push(`${label} mismatch
expected: ${expectedText}
actual:   ${actualText}`);
  }
}

export function comparePrimitive(
  failures: string[],
  label: string,
  expected: unknown,
  actual: unknown
): void {
  if (expected !== actual) {
    failures.push(`${label} expected ${String(expected)} but got ${String(actual)}`);
  }
}
