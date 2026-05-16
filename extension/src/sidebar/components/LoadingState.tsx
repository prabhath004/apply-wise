type LoadingStateProps = {
  label: string;
};

export function LoadingState({ label }: LoadingStateProps) {
  return (
    <div className="rounded-lg border border-border bg-white p-4 text-sm text-muted shadow-sm">
      {label}
    </div>
  );
}
