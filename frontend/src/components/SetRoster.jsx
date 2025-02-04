import React, { useState, useRef } from "react";

const SetRoster = () => {
  const [videogame, setVideogame] = useState("rl");
  const usernameInput = useRef();

  const handleVideogameChange = (event) => {
    setVideogame(event.target.value);
  };

  return (
    <div>
      <h1 className="pt-8 text-center text-3xl font-semibold"> Set Roster </h1>
      <div className="p-8">
        <h2 className="py-8 text-2xl font-semibold">Notice:</h2>
        <ul className="list-disc pl-5 text-custom-off-white">
          <li>Enter the names of all players</li>
          <li>You can only submit your roster once for the season</li>
          <li>Contact the admin if you have issues</li>
        </ul>
      </div>
      <div className="flex flex-col items-center">
        <select
          className="bg-custom-off-white px-8 py-2 font-bold text-black"
          onChange={handleVideogameChange}
          value={videogame}
        >
          <option value="rl"> Rocket League</option>
          <option value="val">Valorant</option>
          <option value="apex">Apex Legends</option>
        </select>

        <div className="flex justify-center p-8">
          <input
            type="text"
            placeholder="Enter username"
            ref={usernameInput}
            className="w-full p-4"
          ></input>
          <button className="bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold">
            Add Player
          </button>
        </div>
        <button className="bg-custom-gold px-8 py-2 font-bold text-black">
          Submit
        </button>
      </div>
    </div>
  );
};

export default SetRoster;
