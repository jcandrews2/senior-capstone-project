import React, { useState, useRef } from "react";
import { useAuth } from "./AuthContext";
import { IoEyeOffSharp, IoEyeSharp } from "react-icons/io5";
import ManageAccounts from "./ManageAccounts";
import SetRoster from "./SetRoster";

const ProfilePage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const usernameInput = useRef();
  const passwordInput = useRef();

  const { username, loggedIn, isAdmin, login, logout } = useAuth();

  const toggleShowPassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="flex min-h-dvh w-full justify-center bg-custom-gray">
      {loggedIn ? (
        <div className="flex flex-col items-center">
          <div className="border-b border-custom-off-white p-8">
            <h1 className="p-8 text-center text-6xl font-semibold">
              {username}
            </h1>
            <div className="flex justify-center p-8">
              <button
                href="mailto:p_hour@coloradocollege.edu"
                className="m-2 bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
              >
                Forgot Password
              </button>
              <button
                className="m-2 bg-custom-gold px-8 py-2 font-bold text-black"
                onClick={logout}
              >
                Logout
              </button>
            </div>
          </div>
          {!isAdmin ? <SetRoster /> : null}
          {isAdmin ? <ManageAccounts /> : null}
        </div>
      ) : (
        <div className="flex w-1/2 flex-col items-center">
          <h1 className="p-8 text-3xl font-semibold"> Login </h1>
          <input
            type="text"
            placeholder="Username"
            ref={usernameInput}
            className="my-4 w-1/2 p-4"
          ></input>
          <div className="relative my-4 w-1/2 text-black">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              ref={passwordInput}
              className="w-full p-4"
            ></input>
            {showPassword ? (
              <IoEyeSharp
                className="absolute right-4 top-1/2 translate-y-[-50%] transform"
                onClick={toggleShowPassword}
              />
            ) : (
              <IoEyeOffSharp
                className="absolute right-4 top-1/2 translate-y-[-50%] transform"
                onClick={toggleShowPassword}
              />
            )}
          </div>
          <button
            className="m-8 bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
            onClick={() =>
              login(usernameInput.current.value, passwordInput.current.value)
            }
          >
            Enter
          </button>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
