import React from "react";

const GameCard = (props) => {
  const { match, teamStats, opponentStats } = props;

  return (
    <div className="font-lato text-custom-off-white w-full p-8">
      <h3 className="p-4 text-center text-2xl font-bold text-white">
        {match.school +
          " " +
          match.teamScore +
          "-" +
          match.opponentScore +
          " " +
          match.opponent}
      </h3>

      <table className="w-full table-auto text-left">
        <thead>
          <tr className="text-white">
            {Object.keys(teamStats[0]).map((header, index) => (
              <th
                key={index}
                className="border-custom-off-white bg-custom-gray border-b p-4"
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
                  className={`${index % 2 === 0 ? "bg-custom-light-gray" : "bg-custom-gray"} border-custom-off-white border-y p-4`}
                >
                  {stat}
                </td>
              ))}
            </tr>
          ))}

          {opponentStats.map((player, index) => (
            <tr key={`opponent-${index}`}>
              {Object.values(player).map((stat, i) => (
                <td
                  key={`opponent-${index}-stat-${i}`}
                  className={`${index % 2 === 0 ? "bg-custom-gray" : "bg-custom-light-gray"} border-custom-off-white border-y p-4`}
                >
                  {stat}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default GameCard;
