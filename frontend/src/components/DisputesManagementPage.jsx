import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_ENDPOINTS } from "../config";

const DisputesManagementPage = () => {
  const [disputes, setDisputes] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // useEffect(() => {
  //   const fetchDisputes = async () => {
  //     try {
  //       const response = await fetch(API_ENDPOINTS.getAllDisputes);
  //       const data = await response.json();
  //       setDisputes(data);
  //       setLoading(false);
  //     } catch (error) {
  //       console.error("Error fetching disputes:", error);
  //       setLoading(false);
  //     }
  //   };

  //   fetchDisputes();
  // }, []);

  // 🔹 Mock Data for UI Testing
  useEffect(() => {
    const mockDisputes = [
      {
        gameId: 1,
        gameType: "Valorant",
        map: "Ascent",
        week: "Week 1",
        school: "Colorado College",
        opponent: "School B",
        disputes: [
          "Player stats are incorrect.",
          "Wrong ACS values recorded for some players.",
        ],
      },
      {
        gameId: 2,
        gameType: "Rocket League",
        map: "Champions Field",
        week: "Week 2",
        school: "School C",
        opponent: "School D",
        disputes: ["Incorrect goal count for Team C."],
      },
      {
        gameId: 3,
        gameType: "Apex Legends",
        code: "ACD123",
        week: "Week 3",
        school: "School X",
        opponent: "School Y",
        disputes: ["Squad placement data mismatch.", "Wrong damage stats."],
      },
    ];

    setTimeout(() => {
      setDisputes(mockDisputes);
      setLoading(false);
    }, 1000);
  }, []);

  // Function to review a dispute (navigate to Modify Page)
  const handleReview = (gameId) => {
    navigate("/modify", { state: { gameId } });
  };

  // Function to resolve a dispute
  const handleResolve = async (gameId) => {
    try {
      const response = await fetch(API_ENDPOINTS.resolveDispute(gameId), {
        method: "POST",
      });

      if (response.ok) {
        setDisputes((prevDisputes) =>
          prevDisputes.filter((dispute) => dispute.gameId !== gameId),
        );
        alert("Dispute resolved successfully!");
      } else {
        alert("Failed to resolve dispute.");
      }
    } catch (error) {
      console.error("Error resolving dispute:", error);
    }
  };

  if (loading)
    return (
      <div className="flex h-screen items-center justify-center bg-custom-blue text-2xl text-white">
        Loading disputes...
      </div>
    );

  return (
    <div className="flex min-h-screen flex-col items-center bg-custom-blue p-8">
      <h1 className="mb-6 text-3xl font-bold text-white">
        Super Admin - Manage Disputes
      </h1>

      {disputes.length === 0 ? (
        <p className="text-white">No disputes to review.</p>
      ) : (
        disputes.map((game) => (
          <div
            key={game.gameId}
            className="mb-6 w-3/4 rounded-lg bg-custom-gray p-4 text-white"
          >
            <h2 className="text-xl font-semibold">
              {game.gameType} - {game.map || game.code}
            </h2>
            <p className="text-custom-off-white">
              {game.school} vs {game.opponent} | Week: {game.week}
            </p>

            {/* Dispute Comments Section */}
            <div className="mt-4 rounded-md bg-custom-light-gray p-4">
              <h3 className="text-lg font-semibold">Dispute Comments:</h3>
              <ul className="list-disc pl-4">
                {game.disputes.map((comment, index) => (
                  <li key={index} className="text-white">
                    {comment}
                  </li>
                ))}
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="mt-4 flex gap-4">
              <button
                className="rounded-md bg-green-500 px-4 py-2 text-white hover:bg-green-600"
                onClick={() => handleReview(game.gameId)}
              >
                Review & Edit
              </button>
              <button
                className="rounded-md bg-red-500 px-4 py-2 text-white hover:bg-red-600"
                onClick={() => handleResolve(game.gameId)}
              >
                Resolve Dispute
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default DisputesManagementPage;
