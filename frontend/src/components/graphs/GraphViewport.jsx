import { useMemo, useRef, useState } from "react";

const MIN_SCALE = 1;
const MAX_SCALE = 3;
const ZOOM_STEP = 0.15;

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export default function GraphViewport({ children, height = 350 }) {
  const containerRef = useRef(null);
  const [scale, setScale] = useState(1);
  const [translate, setTranslate] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const translateStartRef = useRef({ x: 0, y: 0 });

  const panBounds = useMemo(() => {
    const el = containerRef.current;

    if (!el) {
      return { maxX: 0, maxY: 0 };
    }

    const width = el.clientWidth;
    const contentHeight = height;

    return {
      maxX: ((scale - 1) * width) / 2,
      maxY: ((scale - 1) * contentHeight) / 2,
    };
  }, [scale, height]);

  const applyClampedTranslate = (x, y) => {
    setTranslate({
      x: clamp(x, -panBounds.maxX, panBounds.maxX),
      y: clamp(y, -panBounds.maxY, panBounds.maxY),
    });
  };

  const handleWheel = (event) => {
    event.preventDefault();

    const direction = event.deltaY > 0 ? -1 : 1;
    const nextScale = clamp(scale + direction * ZOOM_STEP, MIN_SCALE, MAX_SCALE);

    if (nextScale === MIN_SCALE) {
      setScale(1);
      setTranslate({ x: 0, y: 0 });
      return;
    }

    setScale(nextScale);

    setTranslate((current) => ({
      x: clamp(current.x, -((nextScale - 1) * (containerRef.current?.clientWidth ?? 0)) / 2, ((nextScale - 1) * (containerRef.current?.clientWidth ?? 0)) / 2),
      y: clamp(current.y, -((nextScale - 1) * height) / 2, ((nextScale - 1) * height) / 2),
    }));
  };

  const handleMouseDown = (event) => {
    if (scale === 1) return;

    setIsDragging(true);
    dragStartRef.current = { x: event.clientX, y: event.clientY };
    translateStartRef.current = { ...translate };
  };

  const handleMouseMove = (event) => {
    if (!isDragging) return;

    const dx = event.clientX - dragStartRef.current.x;
    const dy = event.clientY - dragStartRef.current.y;

    applyClampedTranslate(
      translateStartRef.current.x + dx,
      translateStartRef.current.y + dy,
    );
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleMouseLeave = () => {
    setIsDragging(false);
  };

  const zoomIn = () => {
    const nextScale = clamp(scale + ZOOM_STEP, MIN_SCALE, MAX_SCALE);
    setScale(nextScale);
  };

  const zoomOut = () => {
    const nextScale = clamp(scale - ZOOM_STEP, MIN_SCALE, MAX_SCALE);

    if (nextScale === 1) {
      setScale(1);
      setTranslate({ x: 0, y: 0 });
      return;
    }

    setScale(nextScale);
    applyClampedTranslate(translate.x, translate.y);
  };

  const resetView = () => {
    setScale(1);
    setTranslate({ x: 0, y: 0 });
  };

  return (
    <div className="relative w-full">
      <div className="absolute right-3 top-3 z-30 flex gap-2">
        <button
          type="button"
          onClick={zoomOut}
          className="rounded-md border-2 border-white px-2 py-1 font-madimi text-white"
        >
          −
        </button>
        <button
          type="button"
          onClick={zoomIn}
          className="rounded-md border-2 border-white px-2 py-1 font-madimi text-white"
        >
          +
        </button>
        <button
          type="button"
          onClick={resetView}
          className="rounded-md border-2 border-white px-3 py-1 font-madimi text-white"
        >
          reset
        </button>
      </div>

      <div
        ref={containerRef}
        className="relative w-full overflow-hidden"
        style={{ height: `${height}px` }}
        onWheel={handleWheel}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
      >
        <div
          className={`absolute inset-0 flex items-center justify-center ${
            isDragging ? "cursor-grabbing" : scale > 1 ? "cursor-grab" : "cursor-default"
          }`}
          onMouseDown={handleMouseDown}
        >
          <div
            className="flex h-full w-full items-center justify-center transition-transform duration-100"
            style={{
              transform: `translate(${translate.x}px, ${translate.y}px) scale(${scale})`,
              transformOrigin: "center center",
            }}
          >
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}