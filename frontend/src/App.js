import { useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ChildNameGenerator from "./components/ChildNameGenerator";
import { Toaster } from "sonner";

function App() {
  return (
    <div className="App min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<ChildNameGenerator />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;
