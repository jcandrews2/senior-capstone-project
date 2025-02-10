import React from "react";
import DisputeModal from "./DisputeModal";

const GameCard = (props) => {
  const { match, videogame, week } = props;
  const isApex = videogame === "apex";

  console.log(videogame, week);

  return (
    <div className="w-full rounded-md p-8 font-lato text-custom-off-white">
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
                  videogame={videogame}
                  week={week}
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
                  videogame={videogame}
                  week={week}
                  isApex={isApex}
                />
              </div>
            )}

            <div className="overflow-x-auto">
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
                      {Object.values(player).map((stat, idx) => (
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

                  {!isApex &&
                    opponentStats.map((player, index) => (
                      <tr key={`opponent-${index}`}>
                        {Object.values(player).map((stat, idx) => (
                          <td
                            key={`opponent-${idx}-stat-${idx}`}
                            className={`${
                              index % 2 === 0
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

export default GameCard;
