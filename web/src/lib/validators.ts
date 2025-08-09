export function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

export function isBoolean(value: unknown): value is boolean {
  return typeof value === "boolean";
}
