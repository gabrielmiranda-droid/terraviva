type StepperProps = {
  steps: string[];
  current: number;
};

export function Stepper({ steps, current }: StepperProps) {
  return (
    <ol className="grid gap-2 md:grid-cols-4">
      {steps.map((step, index) => {
        const isActive = index === current;
        const isDone = index < current;
        return (
          <li
            key={step}
            className={[
              "rounded-md border px-3 py-2 text-sm transition",
              isActive
                ? "border-field-700 bg-field-50 text-field-900"
                : isDone
                  ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                  : "border-stone-200 bg-white text-stone-600",
            ].join(" ")}
          >
            <span className="block text-xs font-semibold uppercase tracking-normal">Etapa {index + 1}</span>
            <strong className="mt-1 block font-semibold">{step}</strong>
          </li>
        );
      })}
    </ol>
  );
}
