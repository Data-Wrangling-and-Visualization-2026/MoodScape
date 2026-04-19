export default function GraphTabButton({ label, isActive, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "inline-flex items-center justify-center",
        "w-fit",
        "rounded-t-lg rounded-b-none",
        "font-madimi text-black",
        "min-w-[130px] max-w-[400px]",
        "px-4 text-center",
        "whitespace-nowrap",
        "transition-all duration-100 ease-out",
        "border-0 outline-none",
        isActive ? "bg-white h-[60px]" : "bg-green-pastel h-12 hover:h-[60px]",
      ].join(" ")}
    >
      <span className="text-[16px] leading-none">{label}</span>
    </button>
  );
}
