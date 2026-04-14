import { useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";

export default function Dropdown({
  options = [],
  value,
  onChange,
  placeholder,
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // close on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!ref.current?.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={ref} className="relative w-full">
      {/* trigger */}
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex h-12 w-full items-center justify-between rounded-2xl bg-zinc-100 px-5 text-2xl font-black"
      >
        <span className={value ? "text-black" : "text-zinc-500"}>
          {value || placeholder}
        </span>

        {/* arrow */}
        <ChevronDown strokeWidth={4} 
        className={`ml-4 h-5 w-5 transition-transform ${
            open ? "rotate-180" : ""
        }`}
        />
      </button>

      {/* dropdown */}
      {open && (
        <div className="absolute z-10 mt-2 max-h-65 w-full overflow-y-auto rounded-xl bg-white shadow-md">
          {options.map((option) => (
            <div
              key={option}
              onClick={() => {
                onChange(option);
                setOpen(false);
              }}
                className={`cursor-pointer py-3 pr-5 text-xl font-bold hover:bg-green-pastel ${
                value === option
                    ? "border-l-4 border-blue-pastel pl-4"
                    : "pl-5"
                }`}
                >
              {option}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}