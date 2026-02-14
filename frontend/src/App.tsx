import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.tsx";
import Fabric from "./pages/Fabric.tsx";
import Frameworks from "./pages/Frameworks.tsx";
import Sales from "./pages/Sales.tsx";
import Intelligence from "./pages/Intelligence.tsx";
import Deploy from "./pages/Deploy.tsx";
import Partners from "./pages/Partners.tsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/fabric" replace />} />
        <Route path="fabric" element={<Fabric />} />
        <Route path="frameworks" element={<Frameworks />} />
        <Route path="sales" element={<Sales />} />
        <Route path="intelligence" element={<Intelligence />} />
        <Route path="deploy" element={<Deploy />} />
        <Route path="partners" element={<Partners />} />
        <Route path="*" element={<Navigate to="/fabric" replace />} />
      </Route>
    </Routes>
  );
}
