import React, { useState, useRef } from "react";
import { useAuth } from "./AuthContext";
import { IoEyeOffSharp, IoEyeSharp } from "react-icons/io5";
import ManageAccounts from "./ManageAccounts";
import ManageRosters from "./ManageRosters";
import Roster from "./Roster";
import { API_ENDPOINTS } from "../config";

const ProfilePage = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [passkey, setPasskey] = useState(null);
  const [adminUsername, setAdminUsername] = useState(null);
  const usernameInput = useRef();
  const passwordInput = useRef();
  const emailInput = useRef();
  const passwordChangeInput = useRef();
  const passkeyInput = useRef();

  const { username, loggedIn, isAdmin, handleLogin, handleLogout } = useAuth();

  const toggleShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleVerifyAdmin = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.handleGetAdminInfo());
      if (response.ok) {
        const data = await response.json();
        setAdminUsername(data["username"]);
        if (data["email"] === emailInput.current.value) {
          handleForgotPassword();
        } else {
          alert("Email not associated with an admin account.");
        }
      }
    } catch (error) {
      console.error("Error fetching schools:", error);
    }
  };

  const handleChangeAdminPassword = async () => {
    if (passkey !== passkeyInput.current.value) {
      alert("Incorrect passkey.");
      return;
    } else {
      setPasskey(null);
    }

    try {
      const response = await fetch(API_ENDPOINTS.handleChangePassword(), {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: adminUsername,
          password: passwordChangeInput.current.value,
        }),
      });

      if (response.ok) {
        alert("Password updated successfully!");
      } else {
        console.error("Account not found.");
      }
    } catch (error) {
      console.error("Error updating password:", error);
    }
  };

  const handleForgotPassword = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.handleForgotPassword(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: emailInput.current.value,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        alert("You've been sent an email with the recovery passkey.");
        setPasskey(data["passkey"]);
      } else {
        console.error("Username already exists.");
      }
    } catch (error) {
      console.error("Error creating account:", error);
    }
  };

  return (
    <div className="flex min-h-dvh w-full justify-center bg-custom-blue py-16">
      {loggedIn ? (
        <div className="flex flex-col items-center">
          <div className="flex flex-col items-center border-b border-custom-off-white p-8">
            <h1 className="p-8 text-center text-6xl font-semibold">
              {username}
            </h1>

            <button
              className="m-2 bg-custom-gold px-8 py-2 font-bold text-black"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>

          {isAdmin ? (
            <>
              <ManageAccounts /> <ManageRosters />
            </>
          ) : (
            <Roster />
          )}
        </div>
      ) : (
        <div className="flex w-1/2 flex-col items-center">
          <h1 className="py-8 text-3xl font-semibold"> Login </h1>
          <input
            type="text"
            placeholder="Username"
            minLength="5"
            maxLength="20"
            ref={usernameInput}
            className="my-4 w-1/2 p-4 text-black"
          ></input>
          <div className="relative my-4 w-1/2 text-black">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              minLength="5"
              maxLength="40"
              ref={passwordInput}
              className="w-full p-4"
            ></input>

            {showPassword ? (
              <IoEyeSharp
                className="absolute right-4 top-1/2 -translate-y-1/2 transform cursor-pointer"
                onClick={toggleShowPassword}
              />
            ) : (
              <IoEyeOffSharp
                className="absolute right-4 top-1/2 -translate-y-1/2 transform cursor-pointer"
                onClick={toggleShowPassword}
              />
            )}
          </div>
          <div className="flex flex-col items-center justify-center">
            <button
              className="my-8 bg-custom-gold px-8 py-2 font-bold text-black"
              onClick={() =>
                handleLogin(
                  usernameInput.current.value,
                  passwordInput.current.value,
                )
              }
            >
              Enter
            </button>

            <div className="w-3/4 p-4">
              <h2 className="pt-8 text-2xl font-semibold">Forgot Password?</h2>
              <ul className="list-disc p-4 pl-5 text-custom-off-white">
                <li>Contact the admin for them to change it</li>
                <li>
                  If you are the admin, verify your email and you'll be sent a
                  code
                </li>
              </ul>
            </div>

            {passkey ? (
              <div className="p-4">
                <input
                  type="password"
                  placeholder="Enter Passkey"
                  minLength="5"
                  maxLength="40"
                  ref={passkeyInput}
                  className="mr-4 p-2"
                />
                <input
                  type="password"
                  placeholder="Change Password"
                  minLength="5"
                  maxLength="40"
                  ref={passwordChangeInput}
                  className="p-2"
                />
                <button
                  onClick={handleChangeAdminPassword}
                  className="mr-2 bg-custom-gold p-2 px-8 font-bold text-black"
                >
                  Confirm
                </button>
              </div>
            ) : (
              <div className="p-4">
                <div className="flex items-center justify-center">
                  <input
                    type="text"
                    placeholder="Enter Email"
                    minLength="5"
                    maxLength="40"
                    ref={emailInput}
                    className="p-2"
                  />
                  <button
                    className="my-4 bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
                    onClick={handleVerifyAdmin}
                  >
                    Verify
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
