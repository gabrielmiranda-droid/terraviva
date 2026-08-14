import { Search, X } from "lucide-react";

type SearchFieldProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  ariaLabel?: string;
  className?: string;
};

export function SearchField({ value, onChange, placeholder, ariaLabel, className = "" }: SearchFieldProps) {
  return (
    <label className={`relative block ${className}`}>
      <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={17} />
      <input
        aria-label={ariaLabel || placeholder}
        className="form-field pl-9 pr-10"
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      {value ? (
        <button
          aria-label="Limpar busca"
          className="absolute right-1.5 top-1/2 inline-flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-md text-stone-500 transition hover:bg-stone-100 hover:text-stone-800 focus:outline-none focus:ring-2 focus:ring-field-100"
          type="button"
          onClick={() => onChange("")}
        >
          <X size={15} aria-hidden="true" />
        </button>
      ) : null}
    </label>
  );
}
