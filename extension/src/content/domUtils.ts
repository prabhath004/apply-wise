export function textFromSelectors(selectors: string[], root: ParentNode = document): string | null {
  for (const selector of selectors) {
    const node = root.querySelector(selector);
    const value = node?.textContent?.trim();
    if (value) return value.replace(/\s+/g, " ");
  }
  return null;
}

export function textFromManySelectors(selectors: string[], root: ParentNode = document): string {
  const parts = selectors
    .flatMap((selector) => Array.from(root.querySelectorAll(selector)))
    .map((node) => node.textContent?.trim().replace(/\s+/g, " "))
    .filter((value): value is string => Boolean(value));
  return Array.from(new Set(parts)).join("\n");
}
