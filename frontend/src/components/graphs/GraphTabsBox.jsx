import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import GraphTabButton from "../ui/GraphTabButton";
import { GRAPH_TABS } from "../../features/graphs/graphTabs";
import { useGraphTabs } from "../../features/graphs/useGraphTabs";

const ParallelCoordinatesPlot = lazy(() => import("./ParallelCoordinatesPlot"));
const MoodWheel = lazy(() => import("./MoodWheel"));
const HeatmapGraph = lazy(() => import("./HeatmapGraph"));
const LineGraph = lazy(() => import("./LineGraph"));

const DEFAULT_BOX_WIDTH = 700;
const DEFAULT_BOX_HEIGHT = 350;

const OVERLAY_GRAPH_WIDTH = 1000;
const OVERLAY_GRAPH_HEIGHT = 500;

function GraphLoadingFallback() {
  return (
    <div className="flex h-full w-full items-center justify-center text-white">
      <img src="/meymuni.gif" alt="smol monke" className="w-20 h-auto" />
    </div>
  );
}

export default function GraphTabsBox() {
  const { activeTab, setActiveTab } = useGraphTabs();

  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);

  const dragStateRef = useRef({
    startX: 0,
    startY: 0,
    originX: 0,
    originY: 0,
  });

  const graphSize = useMemo(() => {
    if (isOverlayOpen) {
      return {
        width: OVERLAY_GRAPH_WIDTH,
        height: OVERLAY_GRAPH_HEIGHT,
      };
    }

    return {
      width: DEFAULT_BOX_WIDTH,
      height: DEFAULT_BOX_HEIGHT,
    };
  }, [isOverlayOpen]);

  const renderActiveGraph = (boxWidth, boxHeight, options = {}) => {
    const sharedProps = {
      width: boxWidth,
      height: boxHeight,
      ...options,
    };

    switch (activeTab) {
      case "parallel-coordinates-plot":
        return <ParallelCoordinatesPlot {...sharedProps} />;
      case "moodwheel":
        return <MoodWheel {...sharedProps} />;
      case "heatmap":
        return <HeatmapGraph {...sharedProps} />;
      case "line-graph":
        return <LineGraph {...sharedProps} />;
      default:
        return <ParallelCoordinatesPlot {...sharedProps} />;
    }
  };

  const openOverlay = () => {
    setIsOverlayOpen(true);
  };

  const closeOverlay = () => {
    setIsOverlayOpen(false);
  };

  const handlePointerDown = (event) => {
    if (event.button !== 0) return;

    setIsDragging(true);
    dragStateRef.current = {
      startX: event.clientX,
      startY: event.clientY,
      originX: offset.x,
      originY: offset.y,
    };
  };

  const handlePointerMove = (event) => {
    if (!isDragging) return;

    const dx = event.clientX - dragStateRef.current.startX;
    const dy = event.clientY - dragStateRef.current.startY;

    setOffset({
      x: dragStateRef.current.originX + dx,
      y: dragStateRef.current.originY + dy,
    });
  };

  const handlePointerUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (!isOverlayOpen) return;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        closeOverlay();
      }
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("pointerup", handlePointerUp);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [isOverlayOpen]);

  return (
    <>
      <section className="w-full">
        <div className="flex w-full justify-center">
          <div className="w-full max-w-[750px]">
            <div className="flex items-end gap-3 px-4">
              {GRAPH_TABS.map((tab) => (
                <GraphTabButton
                  key={tab.id}
                  label={tab.label}
                  isActive={activeTab === tab.id}
                  onClick={() => setActiveTab(tab.id)}
                />
              ))}
            </div>

            <div
              className={[
                "relative -mt-[1px]",
                "w-full rounded-lg",
                "border-4 border-white",
                "bg-dark-blue",
                "h-[350px]",
                "overflow-hidden",
              ].join(" ")}
            >
              <button
                type="button"
                onClick={openOverlay}
                className="absolute right-3 top-3 z-20 rounded-md border border-white/70 bg-dark-blue/80 px-3 py-1 font-afacad text-sm text-white transition hover:scale-105 hover:bg-white/10"
              >
                Open graph
              </button>

              <div className="flex h-full w-full items-center justify-center">
                {!isOverlayOpen && (
                  <Suspense fallback={<GraphLoadingFallback />}>
                    {renderActiveGraph(graphSize.width, graphSize.height, {
                      compact: true,
                      enableHover: false,
                    })}
                  </Suspense>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {isOverlayOpen && (
        <div
          className="fixed inset-0 z-[999] flex items-center justify-center bg-black/75 p-6"
          onClick={closeOverlay}
        >
          <div
            className="relative flex h-[90vh] w-[92vw] flex-col overflow-hidden rounded-2xl border-4 border-white bg-dark-blue shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-white/20 px-4 py-3">
              <p className="font-afacad text-xl text-white">
                {GRAPH_TABS.find((tab) => tab.id === activeTab)?.label}
              </p>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={closeOverlay}
                  className="rounded-md border border-white/70 px-3 py-1 text-white transition hover:bg-white/10"
                >
                  Close
                </button>
              </div>
            </div>

            <div
              className="relative flex-1 overflow-hidden"
              onPointerMove={handlePointerMove}
              onPointerLeave={handlePointerUp}
            >
              <div
                className="flex h-full w-full items-center justify-center"
                onPointerDown={handlePointerDown}
                style={{ cursor: isDragging ? "grabbing" : "grab" }}
              >
                <div>
                  <Suspense fallback={<GraphLoadingFallback />}>
                    {renderActiveGraph(graphSize.width, graphSize.height, {
                      compact: false,
                      enableHover: true,
                    })}
                  </Suspense>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
