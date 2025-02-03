import React, { useState, useCallback, useEffect, useRef } from "react";
import MatchCard from "./MatchCard";
import PlayerReport from "./PlayerReport";
import { IoSearch } from "react-icons/io5";
import { API_ENDPOINTS } from "../config";

const HomePage = () => {
  const [videogame, setVideogame] = useState("rl");
  const [week, setWeek] = useState("1");
  const [matchReports, setMatchReports] = useState([]);
  const [playerReports, setPlayerReports] = useState([]);
  const [activeMatch, setActiveMatch] = useState(null);
  const searchInput = useRef();

  const handleVideogameChange = (event) => {
    setVideogame(event.target.value);
  };

  const handleWeekChange = (event) => {
    setWeek(event.target.value);
  };

  const toggleActiveMatch = (index) => {
    setActiveMatch(activeMatch === index ? null : index);
  };

  const handleGetPlayerReports = useCallback(async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.getPlayerStats(videogame, searchInput.current.value),
      );

      if (response.ok) {
        const data = await response.json();
        setPlayerReports(data);
      } else {
        console.error("Couldn't find any stats for this player.");
        setPlayerReports([]);
      }
    } catch (error) {
      console.error("Error fetching the player stats:", error);
    }
  }, [videogame]);

  const handleGetMatchReports = useCallback(async () => {
    try {
      const response = await fetch(API_ENDPOINTS.getGameReports(videogame, week));

      if (response.ok) {
        const data = await response.json();
        console.log(data);
        setMatchReports(data);
      } else {
        setMatchReports([]);
        console.error("No stats found.");
      }
    } catch (error) {
      console.error("Error fetching game stats:", error);
    }
  }, [videogame, week]);

  useEffect(() => {
    handleGetMatchReports();
    handleGetPlayerReports();
  }, [videogame, week, handleGetMatchReports, handleGetPlayerReports]);

  return (
    <div
      className={`${
        videogame === "val"
          ? "bg-custom-Val"
          : videogame === "rl"
            ? "bg-custom-RL"
            : "bg-custom-Apex"
      } relative flex min-h-dvh justify-center p-8`}
    >
      <div
        className={`${
          videogame === "val"
            ? "bg-[url(./media/Valorant.jpeg)]"
            : videogame === "rl"
              ? "bg-[url(./media/Rocket_League.jpeg)]"
              : "bg-[url(./media/Apex_Legends.jpeg)]"
        } absolute left-0 top-0 z-0 h-full w-full bg-cover bg-center opacity-40`}
      ></div>

      <div className="relative z-10 flex w-3/4 flex-col items-center">
        <div className="w-full py-16 text-white">
          <h1 className="py-8 text-3xl font-semibold"> Search </h1>

          <div className="flex rounded-md bg-custom-gray p-4">
            <select
              className="mx-2 rounded-md border border-custom-off-white bg-custom-gray py-8"
              onChange={handleVideogameChange}
              value={videogame}
            >
              <option value="rl">Rocket League</option>
              <option value="val">Valorant</option>
              <option value="apex">Apex Legends</option>
            </select>

            <div className="relative w-full text-black">
              <input
                type="text"
                placeholder="Find a player's stats by name"
                className="h-full w-full rounded-md border border-black p-4"
                ref={searchInput}
              />
              <IoSearch
                className="absolute right-4 top-5 h-auto w-12 cursor-pointer"
                onClick={handleGetPlayerReports}
              />
            </div>
          </div>
        </div>

        {playerReports.length > 0 ? (
          <div className="w-full">
            <h2 className="py-8 text-2xl font-semibold">Player Stats</h2>
            <div className="z-30 w-full rounded-md bg-custom-gray">
              <PlayerReport
                player={searchInput.current.value}
                playerReports={playerReports}
              />
            </div>
          </div>
        ) : null}

        <div className="w-full">
          <div className="flex justify-between">
            <h2 className="py-8 text-2xl font-semibold">Match Stats</h2>
            <select
              className="my-4 rounded-md border border-custom-off-white bg-custom-gray text-white"
              onChange={handleWeekChange}
              value={week}
            >
              <option value="1">Week 1</option>
              <option value="2">Week 2</option>
              <option value="3">Week 3</option>
              <option value="4">Week 4</option>
              <option value="5">Week 5</option>
              <option value="6">Week 6</option>
              <option value="avg">Averages</option>
            </select>
          </div>

          <div className="z-30 w-full">
            {matchReports.length > 0 ? (
              matchReports.map((matchReport, index) => (
                <div className="py-8">
                  <button
                    className="h-20 w-full cursor-pointer rounded-md bg-custom-gray text-custom-off-white"
                    onClick={() => toggleActiveMatch(index)}
                  >
                    {videogame === "apex" ? (
                      <h2 className="p-4 text-center text-3xl font-bold text-white">
                        {matchReport.match.school +
                          " " +
                          matchReport.match.points +
                          " Points"}
                      </h2>
                    ) : (
                      <h2 className="p-4 text-center text-3xl font-bold text-white">
                        {matchReport.match.school +
                          " " +
                          matchReport.match.teamScore +
                          " - " +
                          matchReport.match.opponentScore +
                          " " +
                          matchReport.match.opponent}
                      </h2>
                    )}
                  </button>

                  {activeMatch === index && (
                    <div>
                      <MatchCard
                        match={matchReport.match}
                        videogame={videogame}
                      />
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="w-full rounded-md bg-custom-gray">
                <h3 className="p-12 text-center text-xl font-bold">
                  Nothing to see here...
                </h3>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
