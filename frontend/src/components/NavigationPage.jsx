import React from "react";
import { Link } from "react-router-dom";
import { MdLock } from "react-icons/md";
import { useAuth } from "./AuthContext";

const NavigationPage = ({ hamburgerMenu, setHamburgerMenu }) => {
  const { loggedIn, isAdmin } = useAuth();

  return (
    <div
      className={`absolute left-0 top-[7rem] z-40 flex h-dvh w-full justify-center overflow-hidden bg-custom-gray transition-all duration-[500ms] ease-in-out ${
        hamburgerMenu ? "max-h-[2000px]" : "max-h-0"
      }`}
    >
      <div className="py-24">
        <div className="flex flex-col items-center border-r border-custom-off-white px-8">
          <h6> STATS </h6>
          <Link
            className="cursor-pointer p-8 text-5xl text-custom-off-white hover:text-custom-gold"
            to="/"
            onClick={() => setHamburgerMenu(false)}
          >
            Home
          </Link>
          <Link
            className="p-8 text-5xl text-custom-off-white hover:text-custom-gold"
            to="/rankings"
            onClick={() => setHamburgerMenu(false)}
          >
            Rankings
          </Link>
        </div>
      </div>
      <div className="flex flex-col items-center px-8 py-24">
        <h6> CHANGE </h6>
        <div className="flex p-8 text-custom-off-white hover:text-custom-gold">
          <Link
            className="pr-4 text-5xl"
            to="/upload"
            onClick={() => setHamburgerMenu(false)}
          >
            Upload
          </Link>
          {loggedIn ? null : <MdLock className="h-auto w-12" />}
        </div>

        <div className="flex p-8 text-custom-off-white hover:text-custom-gold">
          <Link
            className="pr-4 text-5xl"
            to="/disputes"
            onClick={() => setHamburgerMenu(false)}
          >
            Disputes
          </Link>
          {loggedIn && isAdmin ? null : <MdLock className="h-auto w-12" />}
        </div>
      </div>
    </div>
  );
};

export default NavigationPage;
