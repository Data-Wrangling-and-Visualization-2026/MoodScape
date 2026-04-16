import GraphTabButton from "../ui/GraphTabButton";
import ParallelCoordinatesPlot from "./ParallelCoordinatesPlot";
import MoodWheel from "./MoodWheel";
import HeatmapGraph from "./HeatmapGraph";
import LineGraph from "./LineGraph";
import { GRAPH_TABS } from "../../features/graphs/graphTabs";
import { useGraphTabs } from "../../features/graphs/useGraphTabs";

export default function GraphTabsBox() {
  const { activeTab, setActiveTab } = useGraphTabs();

  const renderActiveGraph = () => {
    switch (activeTab) {
      case "parallel-coordinates-plot":
        return <ParallelCoordinatesPlot />;
      case "moodwheel":
        return <MoodWheel />;
      case "heatmap":
        return <HeatmapGraph />;
      case "line-graph":
        return <LineGraph />;
      default:
        return <ParallelCoordinatesPlot />;
    }
  };

  return (
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
              "min-h-[350px]",
              "px-6 py-6",
            ].join(" ")}
          >
            {renderActiveGraph()}
          </div>
        </div>
      </div>
    </section>
  );
}