// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function buildQueryParams(params: Record<string, any>): URLSearchParams {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    // Ignore undefined, null, and empty strings
    if (value === undefined || value === null || value === '') {
      return;
    }

    // Convert numbers/booleans to strings, keep strings as is
    searchParams.set(key, String(value));
  });

  return searchParams;
}
