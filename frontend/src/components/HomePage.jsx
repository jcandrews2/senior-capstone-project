import React, { useState, useCallback, useEffect, useRef } from "react";
import GameCard from "./GameCard";
import SeasonCard from "./SeasonCard";
import PlayerReport from "./PlayerReport";
import { IoSearch } from "react-icons/io5";
import { API_ENDPOINTS } from "../config";

const HomePage = () => {
  const [videogame, setVideogame] = useState("rl");
  const [week, setWeek] = useState("1");
  const [matchReports, setMatchReports] = useState([]);
  const [playerReports, setPlayerReports] = useState([]);
  const [seasonReports, setSeasonReports] = useState([]);
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

  const handleGetPlayerStats = useCallback(async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleGetPlayerStats(videogame, week),
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

  const handleGetMatchStats = useCallback(async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleGetMatchStats(videogame, week),
      );

      if (response.ok) {
        const data = await response.json();
        setMatchReports(data);
      } else {
        setMatchReports([]);
        console.error("No stats found.");
      }
    } catch (error) {
      console.error("Error fetching game stats:", error);
    }
  }, [videogame, week]);

  const handleGetSeasonStats = useCallback(async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleGetSeasonStats(videogame, week),
      );

      if (response.ok) {
        const data = await response.json();
        setSeasonReports(data);
      } else {
        setSeasonReports([]);
        console.error("No stats found.");
      }
    } catch (error) {
      console.error("Error fetching game stats:", error);
    }
  }, [videogame, week]);

  useEffect(() => {
    if (week !== "avg") {
      handleGetMatchStats();
    } else {
      handleGetSeasonStats();
    }
  }, [
    videogame,
    week,
    handleGetMatchStats,
    handleGetPlayerStats,
    handleGetSeasonStats,
  ]);

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
          videogame
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
                onClick={() => handleGetPlayerStats}
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
            <h2 className="py-8 text-2xl font-semibold">
              {week !== "avg" ? "Match Stats" : "Season Stats"}
            </h2>
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
              <option value="avg">Season</option>
            </select>
          </div>
          {week !== "avg" ? (
            <div className="z-30 w-full">
              {matchReports.length > 0 ? (
                matchReports.map((matchReport, index) => (
                  <>
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
                        <div className="bg-custom-gray">
                          <GameCard
                            match={matchReport.match}
                            videogame={videogame}
                            week={week}
                          />

                          <div className="p-8">
                            <h3 className="p-4 text-2xl font-bold text-white">
                              Weekly Stats
                            </h3>
                            <div className="overflow-x-auto text-custom-off-white">
                              <table className="w-full table-auto text-left">
                                <thead>
                                  <tr className="text-white">
                                    {matchReport.week.length > 0 &&
                                      Object.keys(matchReport.week[0]).map(
                                        (header, index) => (
                                          <th
                                            key={index}
                                            className="border-b border-custom-off-white bg-custom-gray p-4"
                                          >
                                            {header.toUpperCase()}
                                          </th>
                                        ),
                                      )}
                                  </tr>
                                </thead>

                                <tbody>
                                  {matchReport.week.map((player, index) => (
                                    <tr key={`team-${index}`}>
                                      {Object.values(player).map(
                                        (stat, idx) => (
                                          <td
                                            key={`team-${index}-stat-${idx}`}
                                            className={`${
                                              index % 2 === 0
                                                ? "bg-custom-light-gray"
                                                : "bg-custom-gray"
                                            } border-y border-custom-off-white p-4`}
                                          >
                                            {stat}
                                          </td>
                                        ),
                                      )}
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                ))
              ) : (
                <div className="w-full rounded-md bg-custom-gray">
                  <h3 className="p-12 text-center text-xl font-bold">
                    Nothing to see here...
                  </h3>
                </div>
              )}
            </div>
          ) : seasonReports.length > 0 ? (
            seasonReports.map((seasonReport, index) => (
              <>
                <div className="py-8">
                  <button
                    className="h-20 w-full cursor-pointer rounded-md bg-custom-gray text-custom-off-white"
                    onClick={() => toggleActiveMatch(index)}
                  >
                    <h2 className="p-4 text-center text-3xl font-bold text-white">
                      {seasonReport.school}
                    </h2>
                  </button>

                  {activeMatch === index && (
                    <div className="bg-custom-gray">
                      <SeasonCard players={seasonReport.players} />
                    </div>
                  )}
                </div>
              </>
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
  );
};

export default HomePage;
