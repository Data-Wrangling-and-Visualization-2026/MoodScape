import { BrowserRouter, Routes, Route } from "react-router";
import HomePage from "./pages/HomePage";
import Visualization from "./pages/Visualization";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/visualization" element={<Visualization />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
