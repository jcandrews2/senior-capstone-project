import React, { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { IoMdClose } from "react-icons/io";
import { API_ENDPOINTS } from "../config";
import { useAuth } from "./AuthContext";

const DisputeModal = (props) => {
  const [isOpen, setIsOpen] = useState(false);
  const commentInput = useRef();

  const { loggedIn, username, school } = useAuth();
  const { gameStats, teamStats, opponentStats, videogame, week, isApex } =
    props;

  const toggleModal = () => {
    setIsOpen(!isOpen);
  };

  const handleSubmitDispute = async () => {
    try {
      const response = await fetch(
        API_ENDPOINTS.handleSubmitDispute(videogame),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            game_id: gameStats.gameID,
            username: username,
            school: school,
            comment: commentInput.current.value,
            week_number: week,
            game_number: gameStats.gameNumber,
          }),
        },
      );
      if (response.ok) {
        alert("Dispute submitted successfully!");
      }
    } catch (error) {
      console.error("Error submitting dispute:", error);
    }
  };

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
        Review
      </button>

      {isOpen &&
        createPortal(
          <div className="fixed left-0 top-0 z-50 flex h-full w-full justify-center overflow-y-auto bg-custom-gray">
            {/* Close */}
            <button
              className="absolute right-4 top-4 bg-custom-off-white p-2 hover:bg-custom-gold"
              onClick={toggleModal}
            >
              <IoMdClose size={32} />
            </button>

            <div className="flex h-max w-3/4 flex-col items-center p-8">
              <h1 className="py-8 text-3xl font-semibold"> Review </h1>

              {/* Image */}
              <div className="w-full p-4">
                <img
                  src={API_ENDPOINTS.handleGetPicture(
                    videogame,
                    gameStats.gameID,
                  )}
                  alt="End Game Report"
                />
              </div>

              {/* Table */}
              <div className="w-full p-4">
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
                          opponentStats.map((player, index) => (
                            <tr key={`opponent-${index}`}>
                              {Object.values(player).map((stat, i) => (
                                <td
                                  key={`opponent-${index}-stat-${i}`}
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
              </div>

              {loggedIn && (
                <>
                  <div className="p-4">
                    <h2 className="pt-8 text-2xl font-semibold">
                      See an error?
                    </h2>
                    <ul className="list-disc p-4 pl-5 text-custom-off-white">
                      <li>Submit a stat dispute</li>
                      <li>Mention the error in a comment</li>
                      <li>
                        An admin will review it and make changes as needed
                      </li>
                    </ul>

                    <input
                      type="text"
                      placeholder="Comment"
                      ref={commentInput}
                      className="my-4 w-full rounded-md p-8"
                    />
                  </div>
                  <button
                    className="m-2 bg-custom-gold px-8 py-2 font-bold text-black"
                    onClick={() => handleSubmitDispute()}
                  >
                    Submit
                  </button>
                </>
              )}
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
};

export default DisputeModal;
