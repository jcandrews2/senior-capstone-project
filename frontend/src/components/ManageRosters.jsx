import React, { useState, useEffect } from "react";
import { API_ENDPOINTS } from "../config";

const ManageRosters = () => {
  const [videogame, setVideogame] = useState("val");
  const [schools, setSchools] = useState([]);
  const [currentSchool, setCurrentSchool] = useState("Colorado College");
  const [roster, setRoster] = useState([]);

  const handleVideogameChange = (event) => {
    setVideogame(event.target.value);
  };

  const handleSchoolChange = (event) => {
    setCurrentSchool(event.target.value);
  };

  const handleGetSchools = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.handleGetSchools());
      if (response.ok) {
        const data = await response.json();
        setSchools(data);
      }
    } catch (error) {
      console.error("Error fetching schools:", error);
    }
  };

  const handleGetRoster = async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleGetRoster(videogame, currentSchool),
      );
      if (response.ok) {
        const data = await response.json();
        setRoster(data);
      }
    } catch (error) {
      console.error("Error fetching roster:", error);
    }
  };

  const handleDeleteRoster = async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleDeleteRoster(videogame),
        {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            school: currentSchool,
          }),
        },
      );

      if (response.ok) {
        alert("Roster reset successfully!");
        handleGetRoster();
      }
    } catch (error) {
      console.error("Error resetting roster:", error);
    }
  };

  useEffect(() => {
    handleGetSchools();
  }, []);

  useEffect(() => {
    handleGetRoster();
  }, [videogame, currentSchool]);

  return (
    <div className="flex flex-col items-center">
      <h1 className="p-8 text-3xl font-semibold">Manage Rosters</h1>
      <div className="flex justify-center">
        <select
          className="m-4 bg-custom-off-white px-8 py-2 font-bold text-black"
          onChange={handleVideogameChange}
          value={videogame}
        >
          <option value="rl">Rocket League</option>
          <option value="val">Valorant</option>
          <option value="apex">Apex Legends</option>
        </select>

        <select
          className="m-4 bg-custom-off-white px-8 py-2 font-bold text-black"
          onChange={handleSchoolChange}
          value={currentSchool}
        >
          {schools.map((school, index) => (
            <option key={index} value={school}>
              {school}
            </option>
          ))}
        </select>
      </div>

      {roster.length > 0 ? (
        roster.map((player, index) => (
          <div className="py-2">
            <h3 className="font-bold">{player}</h3>
          </div>
        ))
      ) : (
        <h3 className="font-bold">Team hasn't set their roster yet</h3>
      )}

      <button
        className="m-2 bg-custom-gold px-8 py-2 font-bold text-black"
        onClick={handleDeleteRoster}
      >
        Reset Roster
      </button>
    </div>
  );
};

export default ManageRosters;
