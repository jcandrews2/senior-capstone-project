import React, { useState, useEffect } from "react";
import { API_ENDPOINTS } from "../config";

const RankingsPage = () => {
  const [videogame, setVideogame] = useState("val");
  const [rankings, setRankings] = useState([]);

  const handleVideogameChange = (event) => {
    setVideogame(event.target.value);
  };

  const handleGetRankings = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.handleGetRankings(videogame));
      if (response.ok) {
        const data = await response.json();
        console.log(data);
        setRankings(data);
      } else {
        setRankings([]);
      }
    } catch (error) {
      console.error("Error fetching roster:", error);
    }
  };

  useEffect(() => {
    handleGetRankings();
  }, [videogame]);

  return (
    <div className="flex min-h-dvh flex-col items-center bg-custom-blue py-16">
      <h1 className="p-8 text-3xl font-semibold">Rankings</h1>
      <div className="w-1/2 rounded-md bg-custom-gray">
        <div className="flex justify-center">
          <select
            className="m-8 bg-custom-off-white px-8 py-2 font-bold text-black"
            onChange={handleVideogameChange}
            value={videogame}
          >
            <option value="rl">Rocket League</option>
            <option value="val">Valorant</option>
            <option value="apex">Apex Legends</option>
          </select>
        </div>

        {rankings.length > 0 ? (
          <div className="overflow-x-auto p-8 text-custom-off-white">
            <table className="w-full table-auto text-left">
              <thead>
                <tr className="text-white">
                  {Object.keys(rankings[0]).map((header, index) => (
                    <th
                      key={index}
                      className="border-b border-custom-off-white bg-custom-gray p-4"
                    >
                      {header.toUpperCase()}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {rankings.map((ranking, index) => (
                  <tr key={`team-${index}`}>
                    {Object.values(ranking).map((stat, idx) => (
                      <td
                        key={`team-${idx}-stat-${idx}`}
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
        ) : (
          <div className="w-full rounded-md bg-custom-gray">
            <h3 className="p-12 text-center text-xl font-bold">
              Nothing to see here...
            </h3>
          </div>
        )}
      </div>
    </div>
  );
};

export default RankingsPage;
