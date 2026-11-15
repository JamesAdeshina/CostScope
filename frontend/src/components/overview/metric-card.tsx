interface MetricCardProps {
  title: string;
  value: string;
  description: string;
  referencePeriod: string;
}


export function MetricCard({
  title,
  value,
  description,
  referencePeriod,
}: MetricCardProps) {
  return (
    <article className="group rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex h-full flex-col">
        <p className="text-sm font-medium text-zinc-500">
          {title}
        </p>

        <p className="mt-4 text-3xl font-semibold tracking-tight text-zinc-950">
          {value}
        </p>

        <p className="mt-3 text-sm leading-6 text-zinc-600">
          {description}
        </p>

        <div className="mt-auto pt-6">
          <div className="border-t border-zinc-100 pt-4">
            <p className="text-xs font-medium uppercase tracking-wide text-zinc-400">
              Reference period
            </p>

            <p className="mt-1 text-sm font-medium text-zinc-700">
              {referencePeriod}
            </p>
          </div>
        </div>
      </div>
    </article>
  );
}
