import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { IoMdClose } from "react-icons/io";
import { API_ENDPOINTS } from "../config";

const DisputeModal = (props) => {
  const [isOpen, setIsOpen] = useState(false);
  const [picture, setPicture] = useState("");

  const { gameStats, teamStats, opponentStats, isApex } = props;

  const toggleModal = () => {
    setIsOpen(!isOpen);
  };

  const handleGetPicture = async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleGetPicture(gameStats.game_id),
      );

      if (response.ok) {
        const data = await response.json();
        setPicture(data);
      }
    } catch (error) {}
  };

  useEffect(() => {
    handleGetPicture();
  }, []);

  // remove background scrolling if it's open
  useEffect(() => {
    if (isOpen) {
      document.body.classList.add("overflow-hidden");
    } else {
      document.body.classList.remove("overflow-hidden");
    }
  }, [isOpen]);

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
          <div className="fixed left-0 top-0 z-50 flex h-full w-full items-center justify-center overflow-y-auto bg-custom-gray">
            <div className="relative w-3/4 bg-custom-gray p-8">
              {/* Close */}
              <button
                className="fixed right-4 top-4 bg-custom-gold p-2"
                onClick={toggleModal}
              >
                <IoMdClose size={32} />
              </button>

              <div className="h-max overflow-y-auto p-4">
                {/* Image */}
                <div className="w-full">
                  <img src="/game_reports/0.png" alt="End Game Report" />
                </div>

                {/* Table */}
                <div className="mt-4 w-full">
                  <div className="rounded-md bg-custom-gray text-custom-off-white">
                    {isApex ? (
                      <h3 className="p-4 text-2xl font-bold text-white">
                        {"Game " +
                          gameStats.gameNumber +
                          ": " +
                          gameStats.points +
                          " Points"}
                      </h3>
                    ) : (
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
                </div>

                <input type="text" placeholder="Comment" className="h-20" />
                <button> Submit </button>
              </div>
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
};

export default DisputeModal;
