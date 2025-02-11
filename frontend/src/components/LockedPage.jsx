import React from "react";
import { Link } from "react-router-dom";
import { MdLock } from "react-icons/md";

const LockedPage = ({ loggedIn, isAdminPage }) => {
  return loggedIn ? (
    <div className="flex min-h-dvh flex-col items-center bg-custom-gray p-40 text-center text-white">
      <MdLock className="h-auto w-12" />
      <h1 className="p-8 text-3xl font-semibold">
        You must be an admin
        <br />
        to view this page.
      </h1>
    </div>
  ) : (
    <div className="flex min-h-dvh flex-col items-center bg-custom-gray p-40 text-center text-white">
      <MdLock className="h-auto w-12" />
      <h1 className="p-8 text-3xl font-semibold">
        You must be logged in
        <br />
        to view this page.
      </h1>
      <Link
        className="bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
        to="/profile"
      >
        Go to Login
      </Link>
    </div>
  );
};

export default LockedPage;
