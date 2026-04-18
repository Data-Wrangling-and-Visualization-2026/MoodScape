import { useMemo, useRef, useState } from "react";
import { MOOD_OPTIONS } from "../../features/filters/moodOptions";

/**
 * Wheel geometry:
 * - 6 sectors
 * - each sector spans 60 degrees
 * - each sector is divided into 3 equal radial segments
 *
 * IMPORTANT:
 * Right now this component only renders the spinning wheel itself.
 * No SongDataPoint rendering is included yet.
 */

/**
 * Mapping from mood to the exact theme color token names requested by the user.
 *
 * We use Tailwind utility class names that match the names from your theme:
 * - red-pastel
 * - orange-pastel
 * - yellow-pastel
 * - green-pastel
 * - blue-pastel
 * - purple-pastel
 *
 * For lower segments we keep the same color but reduce opacity.
 */
const moodFillClasses = {
  anger: {
    strong: "fill-[#FF7676]",
    default: "fill-red-pastel",
    mid: "fill-[#FF9797]",
    soft: "fill-[#FFBDBD]",
  },
  anticipation: {
    strong: "fill-[#FF9950]",
    default: "fill-orange-pastel",
    mid: "fill-[#FFBC8D]",
    soft: "fill-[#FFCFAD]",
  },
  happiness: {
    strong: "fill-[#FFF757]",
    default: "fill-yellow-pastel",
    mid: "fill-[#FFFA97]",
    soft: "fill-[#FFFCC2]",
  },
  disgust: {
    strong: "fill-[#65FF6B]",
    default: "fill-green-pastel",
    mid: "fill-[#AFFFB2]",
    soft: "fill-[#D1FFD2]",
  },
  sadness: {
    strong: "fill-[#5865FF]",
    default: "fill-blue-pastel",
    mid: "fill-[#8E97FF]",
    soft: "fill-[#B0B6FF]",
  },
  fear: {
    strong: "fill-[#B766FF]",
    default: "fill-purple-pastel",
    mid: "fill-[#D3A0FF]",
    soft: "fill-[#E7CCFF]",
  },
};

/**
 * Converts polar coordinates to cartesian coordinates.
 *
 * cx, cy  -> circle center
 * radius  -> distance from center
 * angle   -> angle in degrees
 *
 * SVG uses:
 * - x axis to the right
 * - y axis downward
 *
 * We subtract 90 degrees so that 0 degrees starts from the top,
 * which is usually more intuitive for circular charts.
 */
function polarToCartesian(cx, cy, radius, angleInDegrees) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180;

  return {
    x: cx + radius * Math.cos(angleInRadians),
    y: cy + radius * Math.sin(angleInRadians),
  };
}

/**
 * Builds an SVG path for a donut-like sector segment
 * between:
 * - innerRadius
 * - outerRadius
 * - startAngle
 * - endAngle
 *
 * This lets us create the 3 radial layers for each mood sector.
 */
function describeRingSegment(cx, cy, innerRadius, outerRadius, startAngle, endAngle) {
  const outerStart = polarToCartesian(cx, cy, outerRadius, startAngle);
  const outerEnd = polarToCartesian(cx, cy, outerRadius, endAngle);

  const innerEnd = polarToCartesian(cx, cy, innerRadius, endAngle);
  const innerStart = polarToCartesian(cx, cy, innerRadius, startAngle);

  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

  return [
    `M ${outerStart.x} ${outerStart.y}`,
    `A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${outerEnd.x} ${outerEnd.y}`,
    `L ${innerEnd.x} ${innerEnd.y}`,
    `A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${innerStart.x} ${innerStart.y}`,
    "Z",
  ].join(" ");
}

/**
 * Returns the angle from the wheel center to the pointer.
 * We use this to calculate how much the user has dragged around the circle.
 */
function getPointerAngle(clientX, clientY, element) {
  const rect = element.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;

  const dx = clientX - cx;
  const dy = clientY - cy;

  return (Math.atan2(dy, dx) * 180) / Math.PI;
}


/**
 * Builds an SVG arc path that text can follow.
 *
 * We use this only for labels.
 * The path sits a little outside the wheel outline,
 * and the text is attached to that path with <textPath>.
 */
function describeArc(cx, cy, radius, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, radius, startAngle);
  const end = polarToCartesian(cx, cy, radius, endAngle);

  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

  return [
    `M ${start.x} ${start.y}`,
    `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${end.x} ${end.y}`,
  ].join(" ");
}

export default function MoodWheel({
    width = 750,
    height = 350,
  }) {
  /**
   * Current wheel rotation in degrees.
   * This rotation is applied to the whole wheel, so labels and sectors move together.
   */
  const [rotation, setRotation] = useState(0);

  /**
   * Stores info while dragging:
   * - whether the wheel is currently being dragged
   * - the angle of the pointer when drag started / last updated
   */
  const dragStateRef = useRef({
    isDragging: false,
    lastPointerAngle: 0,
  });

  /**
   * Ref to the draggable wheel container.
   * Needed to compute pointer angle relative to the wheel center.
   */
  const wheelRef = useRef(null);

  /**
   * Geometry values.
   *
   * The box is wide, but the wheel itself must stay circular,
   * so we make the SVG square and center it inside the box.
   */
  const size = height;
  const center = size / 2;
  const outerRadius = size * 0.36;

  /**
   * 3 equal radial bands:
   * - inner
   * - middle
   * - outer
   */
  const innerRadius = size * 0.06;
  const bandWidth = (outerRadius - innerRadius) / 4;

  /**
   * Sector data for all moods.
   *
   * We keep the order exactly from MOOD_OPTIONS.
   * This order controls the wheel layout.
   *
   * Angles:
   * - each sector spans 60 degrees
   * - we start from -30 so one sector sits centered at the top
   */
  const sectors = useMemo(() => {
    return MOOD_OPTIONS.map((mood, index) => {
      const sectorStart = -30 + index * 60;
      const sectorEnd = sectorStart + 60;

      return {
        mood,
        startAngle: sectorStart,
        endAngle: sectorEnd,
        fills: moodFillClasses[mood],
      };
    });
  }, []);

  /**
   * Starts dragging.
   */
  const handlePointerDown = (event) => {
    if (!wheelRef.current) return;

    event.currentTarget.setPointerCapture(event.pointerId);

    dragStateRef.current.isDragging = true;
    dragStateRef.current.lastPointerAngle = getPointerAngle(
      event.clientX,
      event.clientY,
      wheelRef.current,
    );
  };

  /**
   * Rotates the wheel while dragging.
   *
   * We compute the new pointer angle, compare it to the previous one,
   * and add the difference to the current wheel rotation.
   */
  const handlePointerMove = (event) => {
    if (!dragStateRef.current.isDragging || !wheelRef.current) return;

    const nextPointerAngle = getPointerAngle(
      event.clientX,
      event.clientY,
      wheelRef.current,
    );

    const delta = nextPointerAngle - dragStateRef.current.lastPointerAngle;

    setRotation((prev) => prev + delta);
    dragStateRef.current.lastPointerAngle = nextPointerAngle;
  };

  /**
   * Ends dragging.
   */
  const stopDragging = () => {
    dragStateRef.current.isDragging = false;
  };

  return (
    <div 
      style={{
            '--box-width': `${width}px`,
            '--box-height': `${height}px`,
          }}
      className="flex h-[var(--box-height)] w-[var(--box-width)] items-center justify-center"
    >
      <div
        ref={wheelRef}
        className="relative flex h-[var(--box-height)] w-[var(--box-width)] touch-none items-center justify-center select-none"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={stopDragging}
        onPointerCancel={stopDragging}
        onPointerLeave={stopDragging}
        style={{
          cursor: dragStateRef.current.isDragging ? "grabbing" : "grab",
        }}
      >
        {/* 
          The whole SVG rotates as one block.
          This guarantees that no sector label or future point
          can become detached from the wheel while spinning.
        */}
        <svg
          viewBox={`0 0 ${size} ${size}`}
          className="h-full w-full"
          style={{
            transform: `rotate(${rotation}deg)`,
            transformOrigin: "50% 50%",
          }}
        >
          {/* =========================================================
             6 sectors × 3 radial segments
             ---------------------------------------------------------
             Each sector uses:
             - outer segment -> strongest color
             - middle segment -> lower opacity
             - inner segment -> lower opacity
             ========================================================= */}
          {sectors.map((sector) => {
            const r1 = innerRadius;
            const r2 = innerRadius + bandWidth;
            const r3 = innerRadius + bandWidth * 2;
            const r4 = innerRadius + bandWidth * 3;
            const r5 = outerRadius;

            return (
              <g key={sector.mood}>
                {/* Inner segment */}
                <path
                  d={describeRingSegment(
                    center,
                    center,
                    r1,
                    r2,
                    sector.startAngle,
                    sector.endAngle,
                  )}
                  className={sector.fills.soft}
                />

                {/* Middle segment */}
                <path
                  d={describeRingSegment(
                    center,
                    center,
                    r2,
                    r3,
                    sector.startAngle,
                    sector.endAngle,
                  )}
                  className={sector.fills.mid}
                />

                {/* Outer segment */}
                <path
                  d={describeRingSegment(
                    center,
                    center,
                    r3,
                    r4,
                    sector.startAngle,
                    sector.endAngle,
                  )}
                  className={sector.fills.default}
                />

                <path
                  d={describeRingSegment(
                    center,
                    center,
                    r4,
                    r5,
                    sector.startAngle,
                    sector.endAngle,
                  )}
                  className={sector.fills.strong}
                />
              </g>
            );
          })}

          {/* White center circle */}
          <circle cx={center} cy={center} r={innerRadius} fill="white" />

          {/* White outer outline, weight 4 */}
          <circle
            cx={center}
            cy={center}
            r={outerRadius}
            fill="none"
            stroke="white"
            strokeWidth="8"
          />

          {/* =========================================================
            Mood labels curved around the wheel
            ---------------------------------------------------------
            Each label follows its own invisible arc path.
            This makes the text go around the circle instead of
            sitting as a straight word near the wheel.
            ========================================================= */}
          <defs>
            {sectors.map((sector) => {
              /**
              * Label arc radius:
              * slightly outside the white outline,
              * but still close to the wheel.
              */
              const labelRadius = outerRadius + 10;

              /**
              * We slightly shrink the arc from both sides
              * so the word stays visually centered inside
              * the 60-degree sector and does not touch borders.
              */
              const arcStart = sector.startAngle;
              const arcEnd = sector.endAngle;
              console.log(sector.mood, center, center, labelRadius, arcStart, arcEnd)

              return (
                <path
                  key={`${sector.mood}-label-path`}
                  id={`mood-label-path-${sector.mood}`}
                  d={describeArc(center, center, labelRadius, arcStart, arcEnd)}
                  fill="none"
                />
              );
            })}
          </defs>

          {sectors.map((sector) => (
            <text
              key={`${sector.mood}-label`}
              className="fill-white font-madimi text-[18px]"
              style={{
                letterSpacing: "1.5px",
                textTransform: "uppercase",
              }}
            >
              <textPath
                href={`#mood-label-path-${sector.mood}`}
                startOffset="50%"
                textAnchor="middle"
              >
                {sector.mood.toUpperCase()}
              </textPath>
            </text>
          ))}
        </svg>
      </div>
    </div>
  );
}