import { useAuth } from "./AuthContext";
import LockedPage from "./LockedPage";

const ProtectedRoute = ({ page, isAdminPage }) => {
  const { loggedIn, isAdmin } = useAuth();

  return loggedIn && isAdmin ? (
    page
  ) : loggedIn && !isAdminPage ? (
    page
  ) : (
    <LockedPage loggedIn={loggedIn} isAdminPage={isAdminPage} />
  );
};

export default ProtectedRoute;
