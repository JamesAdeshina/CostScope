import type {
  SourceMetadata,
} from "@/types/api";


interface SourceListProps {
  sources: SourceMetadata[];
}


export function SourceList({
  sources,
}: SourceListProps) {
  return (
    <section
      id="sources"
      className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm"
    >
      <div className="max-w-2xl">
        <p className="text-sm font-medium text-zinc-500">
          Provenance
        </p>

        <h2 className="mt-1 text-xl font-semibold tracking-tight text-zinc-950">
          Data sources
        </h2>

        <p className="mt-2 text-sm leading-6 text-zinc-600">
          CostScope uses official UK public datasets.
          Source identifiers are retained so each
          metric can be traced back to its publisher.
        </p>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {sources.map(
          (source) => (
            <article
              key={
                source.source_code
              }
              className="rounded-xl border border-zinc-100 bg-zinc-50 p-5"
            >
              <p className="text-sm font-semibold text-zinc-950">
                {source.publisher}
              </p>

              <p className="mt-2 text-sm leading-6 text-zinc-600">
                {source.dataset}
              </p>

              <span className="mt-4 inline-flex rounded-md bg-white px-2.5 py-1 font-mono text-xs text-zinc-500 ring-1 ring-inset ring-zinc-200">
                {source.source_code}
              </span>
            </article>
          ),
        )}
      </div>
    </section>
  );
}
