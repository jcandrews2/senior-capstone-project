import React, { useState } from "react";
import { Link } from "react-router-dom";
import { CgProfile } from "react-icons/cg";

import Hamburger from "hamburger-react";
import NavigationPage from "./NavigationPage";

const DesktopNavbar = () => {
  const [hamburgerMenu, setHamburgerMenu] = useState(false);

  return (
    <nav className="sticky top-0 z-50 flex h-[7rem] items-center justify-between bg-custom-dark-gray">
      <Link
        className="cursor-pointer p-4 px-8 font-racing text-4xl font-extrabold text-custom-off-white hover:text-custom-gold"
        to="/"
        onClick={() => setHamburgerMenu(false)}
      >
        AFK
      </Link>

      <div className="flex items-center p-4">
        <Hamburger
          color="#D9D9D9"
          toggled={hamburgerMenu}
          toggle={setHamburgerMenu}
        />
        <Link to="/profile">
          <CgProfile className="h-auto w-16 cursor-pointer p-4 text-custom-off-white" />
        </Link>
      </div>

      <NavigationPage
        hamburgerMenu={hamburgerMenu}
        setHamburgerMenu={setHamburgerMenu}
      />
    </nav>
  );
};

export default DesktopNavbar;
