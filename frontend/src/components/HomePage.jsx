import React, { useState, useCallback, useEffect, useRef } from "react";
import GameCard from "./GameCard";
import SeasonCard from "./SeasonCard";
import PlayerReport from "./PlayerReport";
import { IoSearch } from "react-icons/io5";
import { IoMdClose } from "react-icons/io";
import { API_ENDPOINTS } from "../config";

const HomePage = () => {
  const [videogame, setVideogame] = useState("val");
  const [week, setWeek] = useState("1");
  const [matchReports, setMatchReports] = useState([]);
  const [playerReports, setPlayerReports] = useState([]);
  const [seasonReports, setSeasonReports] = useState([]);
  const [activeMatch, setActiveMatch] = useState(null);
  const searchInput = useRef();

  const handleVideogameChange = (event) => {
    setVideogame(event.target.value);
    setPlayerReports([]);
    searchInput.current.value = "";
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
        API_ENDPOINTS.handleGetPlayerStats(
          videogame,
          searchInput.current.value,
        ),
      );

      if (response.ok) {
        const data = await response.json();
        setPlayerReports(data);
      } else {
        alert("Couldn't find any stats for this player.");
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
        console.error("No match stats found.");
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
        console.error("No season stats found.");
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
    handleGetSeasonStats,
    handleGetPlayerStats,
  ]);

  return (
    <div
      className={`${
        videogame === "val"
          ? "bg-custom-Val"
          : videogame === "rl"
            ? "bg-custom-RL"
            : "bg-custom-Apex"
      } relative flex min-h-dvh w-full justify-center`}
    >
      <div
        className={`${
          videogame
        } absolute left-0 top-0 h-full w-full bg-cover bg-center opacity-30 ${
          videogame === "val"
            ? "bg-custom-Val"
            : videogame === "rl"
              ? "bg-custom-RL"
              : "bg-custom-Apex"
        }`}
      ></div>
      <div className="z-10 flex w-3/4 flex-col items-center py-16">
        <div className="w-full pb-8 text-white">
          <h1 className="py-8 text-3xl font-semibold"> Search </h1>

          <div className="flex rounded-md bg-custom-gray p-4">
            <select
              className="mr-2 rounded-md border border-custom-off-white bg-custom-gray py-8"
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
                minLength="1"
                maxLength="50"
                className="h-full w-full rounded-md p-4"
                ref={searchInput}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleGetPlayerStats();
                  }
                }}
              />

              {playerReports.length > 0 ? (
                <IoMdClose
                  className="absolute right-4 top-5 h-auto w-12 cursor-pointer"
                  onClick={() => setPlayerReports([])}
                />
              ) : (
                <IoSearch
                  className="absolute right-4 top-5 h-auto w-12 cursor-pointer"
                  onClick={handleGetPlayerStats}
                />
              )}
            </div>
          </div>
        </div>

        <div
          className={`w-full overflow-hidden transition-all duration-[500ms] ease-in-out ${
            playerReports.length > 0 ? "max-h-[2000px]" : "max-h-0"
          }`}
        >
          <h2 className="py-8 text-2xl font-semibold">Player Stats</h2>
          <div className="z-30 w-full rounded-md bg-custom-gray">
            {playerReports.length > 0 ? (
              <PlayerReport
                player={searchInput.current.value}
                playerReports={playerReports}
              />
            ) : null}
          </div>
        </div>

        <div className="w-full">
          <div className="flex justify-between">
            <h2 className="py-8 text-2xl font-semibold">
              {week !== "avg" ? "Match Stats" : "Season Stats"}
            </h2>
            <select
              className="my-6 rounded-md border border-custom-off-white bg-custom-gray text-white"
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
                    <div className="mb-4 rounded-md bg-custom-gray">
                      <button
                        className="h-20 w-full cursor-pointer text-custom-off-white"
                        onClick={() => toggleActiveMatch(index)}
                      >
                        {videogame === "apex" ? (
                          <h2 className="p-4 text-center text-3xl font-bold">
                            {matchReport.match.school +
                              " " +
                              matchReport.match.points +
                              " Points"}
                          </h2>
                        ) : (
                          <h2 className="p-4 text-center text-3xl font-bold">
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
                      <div
                        className={`overflow-hidden transition-all duration-[500ms] ease-in-out ${
                          activeMatch === index
                            ? "max-h-[5000px] opacity-100"
                            : "max-h-0 opacity-0"
                        }`}
                      >
                        <GameCard
                          match={matchReport.match}
                          videogame={videogame}
                          week={week}
                        />

                        <div className="p-8">
                          <h3 className="p-4 text-2xl font-bold text-white">
                            {videogame === "apex"
                              ? "Weekly Stats: " +
                                matchReport.match.points +
                                " Points"
                              : "Weekly Stats"}
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
                                    {Object.values(player).map((stat, idx) => (
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
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
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
                <div className="mb-4 rounded-md bg-custom-gray">
                  <button
                    className="h-20 w-full cursor-pointer text-custom-off-white"
                    onClick={() => toggleActiveMatch(index)}
                  >
                    <h2 className="p-4 text-center text-3xl font-bold text-white">
                      {seasonReport.school}
                    </h2>
                  </button>

                  <div
                    className={`overflow-hidden transition-all duration-[500ms] ease-in-out ${
                      activeMatch === index
                        ? "max-h-[2000px] opacity-100"
                        : "max-h-0 opacity-100"
                    }`}
                  >
                    <SeasonCard players={seasonReport.players} />
                  </div>
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
