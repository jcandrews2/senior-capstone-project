import React from "react";

const SeasonCard = ({ players }) => {
  return (
    <div className="m-8 overflow-x-auto text-custom-off-white">
      {players.length > 0 ? (
        <table className="w-full table-auto text-left">
          <thead>
            <tr className="text-white">
              {players.length > 0 &&
                Object.keys(players[0]).map((header, index) => (
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
            {players.map((player, index) => (
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
          </tbody>
        </table>
      ) : (
        <h3 className="p-12 text-center text-xl font-bold">
          Nothing to see here...
        </h3>
      )}
    </div>
  );
};

export default SeasonCard;
