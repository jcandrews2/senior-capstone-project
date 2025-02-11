import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { API_ENDPOINTS } from "../config";

const ModifyPage = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Accept OCR data passed from UploadPage or set default empty structure
  const initialData = location.state?.ocrData || {
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
  };

  const file = location.state?.file || null;
  const [formData, setFormData] = useState(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [imagePreview, setImagePreview] = useState(null);

  // Generate a preview of the image either from file (frontend) or from backend URL
  useEffect(() => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    } else if (formData.image_url) {
      setImagePreview(API_ENDPOINTS.baseURL + formData.image_url);
    }
  }, [file, formData.image_url]);

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
      const response = await fetch(API_ENDPOINTS.uploadMatch, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert("Data submitted successfully!");
        navigate("/");
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

      {/* Editable Match Info */}
      <div className="mb-8 w-3/4 rounded-md bg-custom-gray p-6 text-white shadow-lg">
        <h2 className="mb-4 text-2xl font-semibold">Game Details</h2>

        <div className="flex flex-wrap justify-between">
          <select
            className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
            value={formData.game}
            onChange={(e) => handleInputChange(e, "game")}
          >
            <option value="rocket-league">Rocket League</option>
            <option value="valorant">Valorant</option>
            <option value="apex-legends">Apex Legends</option>
          </select>
          <select
            className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
            value={formData.week}
            onChange={(e) => handleInputChange(e, "week")}
          >
            <option value="1">Week 1</option>
            <option value="2">Week 2</option>
            <option value="3">Week 3</option>
          </select>
          <select
            className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
            value={formData.game_number}
            onChange={(e) => handleInputChange(e, "game_number")}
          >
            <option value="1">Game 1</option>
            <option value="2">Game 2</option>
            <option value="3">Game 3</option>
          </select>
          {formData.game == "valorant" && (
            <input
              type="text"
              value={formData.map}
              placeholder="Map"
              className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
              onChange={(e) => handleInputChange(e, "map")}
            />
          )}
          {formData.game == "apex-legends" && (
            <input
              type="text"
              value={formData.squad_placed}
              placeholder="Squad Placement"
              className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
              onChange={(e) => handleInputChange(e, "squad_placed")}
            />
          )}
          <input
            type="text"
            value={formData.school}
            placeholder="School"
            className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
            onChange={(e) => handleInputChange(e, "school")}
          />
          {formData.game == "valorant" && (
            <input
              type="text"
              value={formData.opponent_school}
              placeholder="Opponent School"
              className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
              onChange={(e) => handleInputChange(e, "opponent_school")}
            />
          )}
          {formData.game == "valorant" && (
            <div>
              <input
                type="text"
                value={formData.w_points}
                placeholder="Winning Points"
                className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
                onChange={(e) => handleInputChange(e, "w_points")}
              />
              <input
                type="text"
                value={formData.l_points}
                placeholder="Losing Points"
                className="mx-2 mb-4 w-[48%] rounded-md border border-custom-off-white bg-custom-gray p-4 text-white"
                onChange={(e) => handleInputChange(e, "l_points")}
              />
            </div>
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
                  <input
                    type="text"
                    value={value}
                    onChange={(e) => handlePlayerChange(e, index, key)}
                    className="w-full rounded-md border border-custom-off-white bg-custom-gray p-2 text-white"
                  />
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

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
