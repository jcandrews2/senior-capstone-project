import React, { useState, useRef, useEffect } from "react";
import { useAuth } from "./AuthContext";
import { API_ENDPOINTS } from "../config";

const Roster = () => {
  const [videogame, setVideogame] = useState("rl");
  const [roster, setRoster] = useState([]);
  const { school } = useAuth();

  const handleVideogameChange = (event) => {
    setVideogame(event.target.value);
  };

  const handleGetRoster = async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleGetRoster(videogame, school),
      );
      if (response.ok) {
        const data = await response.json();
        setRoster(data);
      }
    } catch (error) {
      console.error("Error fetching roster:", error);
    }
  };

  useEffect(() => {
    handleGetRoster();
  }, [videogame, school]);

  return (
    <div className="flex flex-col items-center p-8">
      <h1 className="pt-8 text-center text-3xl font-semibold">Set Roster</h1>
      <select
        className="m-4 bg-custom-off-white px-8 py-2 font-bold text-black"
        onChange={handleVideogameChange}
        value={videogame}
      >
        <option value="rl">Rocket League</option>
        <option value="val">Valorant</option>
        <option value="apex">Apex Legends</option>
      </select>

      {roster.length > 0 ? (
        <div className="flex flex-col items-center p-8">
          <h2 className="py-8 text-2xl font-semibold">Current Roster</h2>
          {roster.map((player, index) => (
            <div key={index} className="py-2">
              <h3 className="font-bold">{player}</h3>
            </div>
          ))}
        </div>
      ) : (
        <SetRoster videogame={videogame} handleGetRoster={handleGetRoster} />
      )}
    </div>
  );
};

const SetRoster = (props) => {
  const [newRoster, setNewRoster] = useState([]);
  const { school } = useAuth();
  const usernameInput = useRef();

  const { videogame, handleGetRoster } = props;

  const handleAddPlayer = (username) => {
    setNewRoster([...newRoster, username]);
  };

  const handleRemovePlayer = (index) => {
    setNewRoster(newRoster.filter((_, idx) => index !== idx));
  };

  const handleSubmitRoster = async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleSubmitRoster(videogame),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            school: school,
            roster: newRoster,
          }),
        },
      );
      if (response.ok) {
        alert("Successfully submitted roster!");
        handleGetRoster();
      }
    } catch (error) {
      console.error("Error submitting roster:", error);
      alert("Failed to submit roster.");
    }
  };

  return (
    <>
      <div className="p-8">
        <h2 className="py-8 text-2xl font-semibold">Notice:</h2>
        <ul className="list-disc pl-5 text-custom-off-white">
          <li>
            You still need to submit your
            {videogame === "rl"
              ? " Rocket League "
              : videogame === "val"
                ? " Valorant "
                : " Apex Legends "}
            roster for this season
          </li>
          <li>Enter the gamertags of all participating players</li>
          <li>You can only submit it once per season</li>
          <li>Contact the admin if you have issues</li>
        </ul>
      </div>

      <div className="flex flex-col items-center">
        {newRoster.length > 0 && (
          <div className="flex w-3/4 flex-col items-center p-8">
            <h2 className="py-8 text-2xl font-semibold">Roster</h2>
            {newRoster.map((player, index) => (
              <div key={index} className="flex w-full justify-between p-2">
                <h3 className="p-2 font-bold">{player}</h3>
                <button
                  className="bg-custom-off-white p-2 font-bold text-black hover:bg-custom-gold"
                  onClick={() => handleRemovePlayer(index)}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="flex justify-center p-8">
          <input
            type="text"
            placeholder="Enter username"
            ref={usernameInput}
            className="w-full p-4"
          ></input>
          <button
            className="bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
            onClick={() => handleAddPlayer(usernameInput.current.value)}
          >
            Add Player
          </button>
        </div>
        <button
          className="bg-custom-gold px-8 py-2 font-bold text-black"
          onClick={handleSubmitRoster}
        >
          Submit
        </button>
      </div>
    </>
  );
};

export default Roster;
