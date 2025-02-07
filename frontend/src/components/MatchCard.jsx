import React from "react";
import DisputeModal from "./DisputeModal";

const MatchCard = (props) => {
  const { match, videogame } = props;
  const isApex = videogame === "apex";

  return (
    <div className="mb-16 w-full rounded-md bg-custom-gray p-8 font-lato text-custom-off-white">
      {match.games.map((game, index) => {
        const gameStats = game.gameStats;
        const teamStats = game.teamStats || [];
        const opponentStats = game.opponentStats || [];

        return (
          <div key={index} className="mb-8">
            {isApex ? (
              <div className="flex justify-between">
                <h3 className="p-4 text-2xl font-bold text-white">
                  {"Game " +
                    gameStats.gameNumber +
                    ": " +
                    gameStats.points +
                    " Points"}
                </h3>
                <DisputeModal
                  gameStats={gameStats}
                  teamStats={teamStats}
                  opponentStats={opponentStats}
                  isApex={isApex}
                />
              </div>
            ) : (
              <div className="flex justify-between">
                <h3 className="p-4 text-2xl font-bold text-white">
                  {"Game " +
                    gameStats.gameNumber +
                    ": " +
                    gameStats.school +
                    " " +
                    gameStats.teamScore +
                    " - " +
                    gameStats.opponentScore +
                    " " +
                    gameStats.opponent}
                </h3>
                <DisputeModal
                  gameStats={gameStats}
                  teamStats={teamStats}
                  opponentStats={opponentStats}
                  isApex={isApex}
                />
              </div>
            )}

            <div className="overflow-x-scroll">
              <table className="w-full table-auto text-left">
                <thead>
                  <tr className="text-white">
                    {teamStats.length > 0 &&
                      Object.keys(teamStats[0]).map((header, index) => (
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
                  {teamStats.map((player, index) => (
                    <tr key={`team-${index}`}>
                      {Object.values(player).map((stat, i) => (
                        <td
                          key={`team-${index}-stat-${i}`}
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

                  {!isApex &&
                    opponentStats.map((player, idx) => (
                      <tr key={`opponent-${idx}`}>
                        {Object.values(player).map((stat, i) => (
                          <td
                            key={`opponent-${idx}-stat-${i}`}
                            className={`${
                              idx % 2 === 0
                                ? "bg-custom-gray"
                                : "bg-custom-light-gray"
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
        );
      })}
    </div>
  );
};

export default MatchCard;
