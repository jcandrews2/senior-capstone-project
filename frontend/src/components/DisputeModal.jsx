import React, { useState } from "react";
import { createPortal } from "react-dom";
import { IoMdClose } from "react-icons/io";

const DisputeModal = (props) => {
  const [isOpen, setIsOpen] = useState(false);

  const { gameStats, teamStats, opponentStats, isApex } = props;

  const toggleModal = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="z-50">
      <button
        className="m-2 bg-custom-off-white px-8 py-2 font-bold text-black hover:bg-custom-gold"
        onClick={toggleModal}
      >
        Dispute
      </button>

      {isOpen &&
        createPortal(
          <div className="fixed left-0 top-0 z-50 flex h-dvh w-full items-center justify-center bg-black bg-opacity-80">
            <button
              className="absolute right-0 top-0 m-4 bg-custom-off-white px-8 py-2 hover:bg-custom-gold"
              onClick={toggleModal}
            >
              <IoMdClose size={32} />
            </button>

            <div className="mb-8 rounded-md bg-custom-gray text-custom-off-white">
              {isApex ? (
                <div className="flex justify-between">
                  <h3 className="p-4 text-2xl font-bold text-white">
                    {"Game " +
                      gameStats.gameNumber +
                      ": " +
                      gameStats.points +
                      " Points"}
                  </h3>
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
          </div>,
          document.body,
        )}
    </div>
  );
};

export default DisputeModal;
