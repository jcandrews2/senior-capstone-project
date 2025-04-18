import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { API_ENDPOINTS } from "../config";

const ModifyPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Accept OCR data passed from UploadPage or set default empty structure
  const initialData = location.state?.ocrData || {
    game_id: "",
    image_url: "",
    game: "",
    week: "",
    school: "",
    opponent_school: "",
    map: "",
    code: "",
    squad_placed: "",
    players: [],
    game_number: "",
    did_win: "1",
    w_points: "",
    l_points: "",
    disputes: [],
  };

  const file = location.state?.file || null;
  const [formData, setFormData] = useState(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [imagePreview, setImagePreview] = useState(null);
  const [roster, setRoster] = useState([]);

  // Generate a preview of the image either from file (frontend) or from backend URL
  useEffect(() => {
    const getRoster = async () => {
      let videogame =
        formData.game === "valorant"
          ? "val"
          : formData.game === "apex-legends"
            ? "apex"
            : formData.game === "rocket-league"
              ? "rl"
              : null;

      if (!videogame || !formData.school) return;

      try {
        const response = await fetch(
          API_ENDPOINTS.handleGetRoster(videogame, formData.school),
        );
        if (response.ok) {
          const data = await response.json();
          setRoster(data);
        }
      } catch (err) {
        console.error("Error fetching roster:", err);
      }
    };

    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    } else if (formData.game_id) {
      setImagePreview(`${API_ENDPOINTS.handleGetPicture(formData.game_id)}`);
    }

    if (formData.game_id) getRoster();
  }, [file, formData.game_id, formData.game, formData.school]);

  useEffect(() => {
    console.log(roster);
  }, [roster]);

  // Update handler for editable fields
  const handleInputChange = (event, key) => {
    setFormData({ ...formData, [key]: event.target.value });
  };

  // Update handler for player stats
  const handlePlayerChange = (event, index, key) => {
    const updatedPlayers = [...formData.players];
    updatedPlayers[index][key] = event.target.value;
    setFormData({ ...formData, players: updatedPlayers });
  };

  // Submit modified data to the backend
  const handleGame = async () => {
    setLoading(true);
    try {
      // Check if we're handling a dispute (game_id already exists)
      const isDisputeEdit = formData.disputes && formData.disputes.length > 0;
      console.log(
        `Submitting data ${isDisputeEdit ? "from dispute edit" : "from new upload"}`,
      );

      // Ensure image_url is set correctly
      if (!formData.image_url && formData.game_id) {
        formData.image_url = API_ENDPOINTS.handleGetPicture(formData.game_id);
      }

      const response = await fetch(API_ENDPOINTS.uploadMatch, {
        method: "POST", // Always use POST as the backend handles both cases
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        // Different message based on source
        const successMessage = isDisputeEdit
          ? "Dispute resolved successfully! Data updated."
          : "Data submitted successfully!";
        alert(successMessage);

        // Redirect to home or disputes page based on source
        navigate(isDisputeEdit ? "/disputes" : "/");
      } else {
        const errorData = await response.json();
        setError(errorData.error || "Failed to submit data.");
      }
    } catch (err) {
      console.error("Error submitting data:", err);
      setError("An error occurred while submitting the data.");
    } finally {
      setLoading(false);
    }
  };

  if (loading)
    return (
      <div className="flex h-screen items-center justify-center bg-custom-blue text-2xl text-white">
        Processing...
      </div>
    );

  if (!formData || !formData.players || formData.players.length === 0)
    return (
      <div className="flex h-screen items-center justify-center bg-custom-blue text-2xl text-white">
        No data available. Please upload data first.
      </div>
    );

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-custom-blue p-8">
      <h1 className="mb-8 text-4xl font-bold text-white">Modify Game Data</h1>

      {/* Display the uploaded image from file or backend URL */}
      {imagePreview ? (
        <div className="mb-6 w-3/4">
          <h2 className="text-xl font-semibold text-white">Uploaded Image</h2>
          <img
            src={imagePreview}
            alt="Uploaded Match Screenshot"
            className="mt-4 w-full rounded-lg border-2 border-custom-off-white shadow-lg"
          />
        </div>
      ) : (
        <p className="text-white">No image available</p>
      )}

      {/* Display error messages if any */}
      {error && (
        <div className="mb-6 w-3/4 rounded bg-red-100 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Display disputes if any */}
      {formData.disputes && formData.disputes.length > 0 && (
        <div className="mb-6 w-3/4 rounded-md bg-red-100 p-4 text-red-700 shadow-lg">
          <h2 className="text-xl font-semibold text-black">Disputes:</h2>
          <ul className="list-disc pl-4">
            {formData.disputes.map((dispute, index) => (
              <li key={index}>
                <strong>
                  {dispute.username} ({dispute.school}):
                </strong>{" "}
                {dispute.comment}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Editable Match Info */}
      <div className="mb-8 w-3/4 rounded-md bg-custom-gray p-6 text-white shadow-lg">
        <h2 className="mb-4 text-2xl font-semibold">Game Details</h2>

        <div className="flex flex-wrap justify-between">
          <div className="mx-2 mb-4 w-[48%]">
            <label className="mb-2 block text-sm font-medium">Game Type</label>
            <select
              className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
              value={formData.game}
              onChange={(e) => handleInputChange(e, "game")}
            >
              <option value="rocket-league">Rocket League</option>
              <option value="valorant">Valorant</option>
              <option value="apex-legends">Apex Legends</option>
            </select>
          </div>

          <div className="mx-2 mb-4 w-[48%]">
            <label className="mb-2 block text-sm font-medium">Week</label>
            <select
              className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
              value={formData.week}
              onChange={(e) => handleInputChange(e, "week")}
            >
              <option value="1">Week 1</option>
              <option value="2">Week 2</option>
              <option value="3">Week 3</option>
            </select>
          </div>

          <div className="mx-2 mb-4 w-[48%]">
            <label className="mb-2 block text-sm font-medium">
              Game Number
            </label>
            <select
              className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
              value={formData.game_number}
              onChange={(e) => handleInputChange(e, "game_number")}
            >
              <option value="1">Game 1</option>
              <option value="2">Game 2</option>
              <option value="3">Game 3</option>
            </select>
          </div>

          {formData.game === "valorant" && (
            <div className="mx-2 mb-4 w-[48%]">
              <label className="mb-2 block text-sm font-medium">Map</label>
              <input
                type="text"
                value={formData.map}
                placeholder="Map"
                className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
                onChange={(e) => handleInputChange(e, "map")}
              />
            </div>
          )}

          {formData.game === "apex-legends" && (
            <div className="mx-2 mb-4 w-[48%]">
              <label className="mb-2 block text-sm font-medium">
                Squad Placement
              </label>
              <input
                type="text"
                value={formData.squad_placed}
                placeholder="Squad Placement"
                className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
                onChange={(e) => handleInputChange(e, "squad_placed")}
              />
            </div>
          )}

          <div className="mx-2 mb-4 w-[48%]">
            <label className="mb-2 block text-sm font-medium">School</label>
            <input
              type="text"
              value={formData.school}
              placeholder="School"
              className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
              onChange={(e) => handleInputChange(e, "school")}
            />
          </div>

          {formData.game === "valorant" && (
            <div className="mx-2 mb-4 w-[48%]">
              <label className="mb-2 block text-sm font-medium">
                Opponent School
              </label>
              <input
                type="text"
                value={formData.opponent_school}
                placeholder="Opponent School"
                className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
                onChange={(e) => handleInputChange(e, "opponent_school")}
              />
            </div>
          )}

          {formData.game === "valorant" && (
            <>
              <div className="mx-2 mb-4 w-[48%]">
                <label className="mb-2 block text-sm font-medium">
                  Winning Points
                </label>
                <input
                  type="text"
                  value={formData.w_points}
                  placeholder="Winning Points"
                  className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
                  onChange={(e) => handleInputChange(e, "w_points")}
                />
              </div>
              <div className="mx-2 mb-4 w-[48%]">
                <label className="mb-2 block text-sm font-medium">
                  Losing Points
                </label>
                <input
                  type="text"
                  value={formData.l_points}
                  placeholder="Losing Points"
                  className="w-full rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
                  onChange={(e) => handleInputChange(e, "l_points")}
                />
              </div>
            </>
          )}
        </div>
      </div>

      {/* Editable Player Data */}
      <div className="w-3/4">
        <h2 className="mb-4 text-2xl font-semibold text-white">Player Stats</h2>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {formData.players.map((player, index) => (
            <div
              key={index}
              className="rounded-lg border bg-custom-gray p-6 text-white shadow-lg"
            >
              <h3 className="mb-4 text-xl font-bold">{player.name}</h3>
              {Object.entries(player).map(([key, value]) => (
                <div key={key} className="mb-3">
                  <label className="block text-sm font-medium capitalize">
                    {key}
                  </label>
                  {key === "name" && formData.game === "apex-legends" ? (
                    <select
                      value={player.name || ""}
                      onChange={(e) => handlePlayerChange(e, index, "name")}
                      className="w-full rounded-md border border-custom-off-white bg-custom-gray p-2 text-white"
                    >
                      <option value="" disabled>
                        Select Player
                      </option>
                      {roster.map((rosterPlayer) => (
                        <option key={rosterPlayer} value={rosterPlayer}>
                          {rosterPlayer}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => handlePlayerChange(e, index, key)}
                      className="w-full rounded-md border border-custom-off-white bg-custom-gray p-2 text-white"
                    />
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <button
        className="mt-8 rounded-lg bg-custom-off-white px-6 py-3 text-black transition hover:bg-custom-gold"
        onClick={handleGame}
      >
        {loading ? "Submitting..." : "Submit"}
      </button>
    </div>
  );
};

export default ModifyPage;
