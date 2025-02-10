import React, { useState, useEffect, useRef } from "react";
import { IoEyeOffSharp, IoEyeSharp } from "react-icons/io5";
import ModifyAccount from "./ModifyAccount";
import { API_ENDPOINTS } from "../config";

const ManageAccounts = () => {
  const [accounts, setAccounts] = useState([]);
  const [showPassword, setShowPassword] = useState(false);
  const usernameInput = useRef();
  const passwordInput = useRef();
  const schoolInput = useRef();

  const toggleShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleGetAccounts = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.handleGetAccounts());

      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
      } else {
        setAccounts([]);
        console.error("No accounts found.");
      }
    } catch (error) {
      console.error("Error fetching accounts:", error);
    }
  };

  const handleCreateAccount = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.handleCreateAccount(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: usernameInput.current.value,
          password: passwordInput.current.value,
          school: schoolInput.current.value,
        }),
      });

      if (response.ok) {
        alert("Account created successfully!");
        handleGetAccounts();
      } else {
        console.error("Username already exists.");
      }
    } catch (error) {
      console.error("Error creating account:", error);
    }
  };

  useEffect(() => {
    handleGetAccounts();
  }, []);

  return (
    <>
      <div className="flex flex-col items-center p-8">
        <h1 className="p-8 text-3xl font-semibold"> Create Account </h1>
        <input
          type="text"
          placeholder="School"
          minlength="5"
          maxlength="20"
          ref={schoolInput}
          className="my-4 w-full p-4 text-black"
        ></input>
        <input
          type="text"
          placeholder="Username"
          minlength="5"
          maxlength="20"
          ref={usernameInput}
          className="my-4 w-full p-4 text-black"
        ></input>
        <div className="relative my-4 w-full text-black">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            minlength="5"
            maxlength="40"
            ref={passwordInput}
            className="w-full p-4"
          ></input>

          {showPassword ? (
            <IoEyeSharp
              className="absolute right-4 top-1/2 translate-y-[-50%] transform cursor-pointer"
              onClick={toggleShowPassword}
            />
          ) : (
            <IoEyeOffSharp
              className="absolute right-4 top-1/2 translate-y-[-50%] transform cursor-pointer"
              onClick={toggleShowPassword}
            />
          )}
        </div>
        <button
          className="m-8 bg-custom-gold px-8 py-2 font-bold text-black"
          onClick={handleCreateAccount}
        >
          Enter
        </button>
      </div>

      {accounts.length > 0 ? (
        <>
          <h1 className="p-8 text-3xl font-semibold">Modify Accounts</h1>

          <div className="rounded-md bg-custom-gray">
            {accounts.map((account, index) => (
              <ModifyAccount
                key={index}
                username={account.username}
                handleGetAccounts={handleGetAccounts}
              />
            ))}
          </div>
        </>
      ) : null}
    </>
  );
};

export default ManageAccounts;
