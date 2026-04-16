import { useState } from "react";

export function useGraphTabs(defaultTabId = "parallel-coordinates-plot") {
  const [activeTab, setActiveTab] = useState(defaultTabId);

  return {
    activeTab,
    setActiveTab,
  };
}