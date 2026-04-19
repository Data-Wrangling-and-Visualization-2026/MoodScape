import { useState } from "react";

export function useGraphTabs(defaultTabId = "moodwheel") {
  const [activeTab, setActiveTab] = useState(defaultTabId);

  return {
    activeTab,
    setActiveTab,
  };
}