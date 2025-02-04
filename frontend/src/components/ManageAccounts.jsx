import React, { useState, useEffect, useRef } from "react";
import ModifyAccount from "./ModifyAccount";

const ManageAccounts = () => {
  const [accounts, setAccounts] = useState([]);
  const usernameInput = useRef();
  const passwordInput = useRef();
  const schoolInput = useRef();

  const handleGetAccounts = async () => {
    try {
      const response = await fetch(`http://40.85.147.30:8080/accounts`);

      if (response.ok) {
        const data = await response.json();
        console.log(data);
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
      const response = await fetch("http://40.85.147.30:8080/accounts", {
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
          ref={schoolInput}
          className="m-8 w-full border border-black p-4"
        ></input>
        <input
          type="text"
          placeholder="Username"
          ref={usernameInput}
          className="m-8 w-full border border-black p-4"
        ></input>
        <input
          type="text"
          placeholder="Password"
          ref={passwordInput}
          className="m-8 w-full border border-black p-4"
        ></input>
        <button
          className="m-2 bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
          onClick={handleCreateAccount}
        >
          Enter
        </button>
      </div>

      {accounts.length > 0 ? (
        <>
          <h1 className="p-8 text-3xl font-semibold">Modify Accounts</h1>
          {accounts.map((account, index) => (
            <ModifyAccount
              key={index}
              username={account.username}
              handleGetAccounts={handleGetAccounts}
            />
          ))}
        </>
      ) : null}
    </>
  );
};

export default ManageAccounts;
