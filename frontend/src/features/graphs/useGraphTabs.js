import { useState } from "react";

export function useGraphTabs(defaultTabId = "heatmap") {
  const [activeTab, setActiveTab] = useState(defaultTabId);

  return {
    activeTab,
    setActiveTab,
  };
}