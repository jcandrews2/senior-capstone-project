import "./App.css";
import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import HomePage from "./components/HomePage";
import UploadPage from "./components/UploadPage";
import RankingsPage from "./components/RankingsPage";
import ProtectedRoute from "./components/ProtectedRoute";
import ModifyPage from "./components/ModifyPage";
import Footer from "./components/Footer";
import ProfilePage from "./components/ProfilePage";
import DisputesManagementPage from "./components/DisputesManagementPage";

function App() {
  return (
    <div className="app">
      <Navbar />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/rankings" element={<RankingsPage />} />
        <Route
          path="/upload"
          element={<ProtectedRoute page={<UploadPage />} />}
        />
        <Route
          path="/disputes"
          element={<ProtectedRoute page={<DisputesManagementPage />} />}
        />
        <Route
          path="/modify"
          element={<ProtectedRoute page={<ModifyPage />} />}
        />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>

      <Footer />
    </div>
  );
}

export default App;
