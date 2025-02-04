import React from "react";

const PlayerReport = (props) => {
  const { player, playerReports } = props;

  return (
    <div className="w-full p-8 font-lato text-custom-off-white">
      <h3 className="p-4 text-center text-2xl font-bold text-white">
        {`${player} Stats Report`}
      </h3>

      <div className="overflow-x-scroll">
        <table className="w-full table-auto text-left">
          <thead>
            <tr className="text-white">
              {Object.keys(playerReports[0]).map((header, index) => (
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
            {playerReports.map((playerReport, index) => (
              <tr key={`player-${index}`}>
                {Object.values(playerReport).map((stat, i) => (
                  <td
                    key={`player-${index}-stat-${i}`}
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
  );
};

export default PlayerReport;
