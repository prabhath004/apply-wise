import type { FitScore } from "../lib/types";

type ScoreCardProps = {
  score: FitScore;
};

export function ScoreCard({ score }: ScoreCardProps) {
  const items = Object.entries(score.breakdown);
  return (
    <section className="rounded-lg border border-border bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold">Fit Score</h2>
          <p className="mt-1 text-xs text-muted">{score.recommendation}</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-semibold text-primary">{score.overall}</div>
          <div className="text-xs text-muted">out of 100</div>
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
