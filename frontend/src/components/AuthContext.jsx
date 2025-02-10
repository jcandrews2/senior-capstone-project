import React, { useState, createContext, useContext } from "react";
import { API_ENDPOINTS } from "../config";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [school, setSchool] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  const handleLogin = async (username, password) => {
    try {
      const response = await fetch(API_ENDPOINTS.handleLogin(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setLoggedIn(true);
        setUsername(data[0]["username"]);
        setSchool(data[0]["school"]);
        if (data[0]["isAdmin"]) {
          setIsAdmin(true);
        }
      } else {
        alert("No account found with these credentials.");
      }
    } catch (error) {
      console.error("Invalid credentials.", error);
    }
  };

  const handleLogout = () => {
    setLoggedIn(false);
    setUsername("");
    setIsAdmin(false);
  };

  return (
    <AuthContext.Provider
      value={{ username, school, loggedIn, isAdmin, handleLogin, handleLogout }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
