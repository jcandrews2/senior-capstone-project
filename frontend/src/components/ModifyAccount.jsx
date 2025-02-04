import React, { useRef } from "react";
import { API_ENDPOINTS } from "../config";

const ModifyAccount = (props) => {
  const { username, handleGetAccounts } = props;
  const passwordChangeInput = useRef();

  const handleChangePassword = async (password) => {
    try {
      const response = await fetch(API_ENDPOINTS.handleChangePassword(), {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
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

  const handleDeleteAccount = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.handleDeleteAccount(), {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
        }),
      });

      if (response.ok) {
        alert("Account deleted successfully!");
        handleGetAccounts();
      }
    } catch (error) {
      console.error("Error deleting account:", error);
    }
  };

  return (
    <div className="flex items-center justify-center p-2">
      <h3 className="p-4 font-bold">{username}</h3>
      <div className="p-4">
        <input
          type="password"
          placeholder="Change Password"
          ref={passwordChangeInput}
          className="p-2"
        />
        <button
          onClick={handleChangePassword}
          className="mr-2 bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
        >
          Confirm
        </button>
      </div>

      <button
        onClick={handleDeleteAccount}
        className="m-2 bg-custom-gold px-8 py-2 font-bold text-black"
      >
        Delete Account
      </button>
    </div>
  );
};

export default ModifyAccount;
