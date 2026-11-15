export function formatCurrency(
  value: number,
): string {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatPercent(
  value: number | null,
  digits = 1,
): string {
  if (value === null) {
    return "—";
  }

  return `${value.toFixed(digits)}%`;
}

export function formatDate(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    "en-GB",
    {
      month: "short",
      year: "numeric",
    },
  ).format(
    new Date(`${value}T00:00:00`),
  );
}
