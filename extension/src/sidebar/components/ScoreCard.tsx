import type { FitScore } from "../lib/types";

type ScoreCardProps = {
  score: FitScore;
};

export function ScoreCard({ score }: ScoreCardProps) {
  const items = Object.entries(score.breakdown);
  const ringStyle = {
    background: `conic-gradient(#2251d1 ${score.overall * 3.6}deg, #e8edf5 0deg)`
  };

  return (
    <section className="rounded-lg border border-border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <h2 className="text-sm font-semibold">Fit Score</h2>
          <p className="mt-1 text-xs leading-5 text-muted">Holistic resume-to-role evaluation</p>
          <span className="mt-3 inline-flex rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 text-xs font-semibold text-primary">
            {score.recommendation}
          </span>
        </div>
        <div className="grid h-24 w-24 shrink-0 place-items-center rounded-full p-2" style={ringStyle}>
          <div className="grid h-full w-full place-items-center rounded-full bg-white">
            <div className="text-center">
              <div className="text-2xl font-semibold text-ink">{score.overall}</div>
              <div className="text-[11px] text-muted">/ 100</div>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-4 space-y-2">
        {items.map(([label, value]) => (
          <div key={label}>
            <div className="mb-1 flex justify-between text-xs">
              <span className="capitalize text-muted">{label}</span>
              <span className="font-medium">{value}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-surface">
              <div className="h-full bg-primary" style={{ width: `${value}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
