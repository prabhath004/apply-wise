export function joinList(values: string[], fallback: string): string {
  return values.length ? values.join(", ") : fallback;
}

export function confidenceLabel(value: number): string {
  if (value >= 85) return "High";
  if (value >= 60) return "Medium";
  if (value > 0) return "Low";
  return "Unknown";
}
