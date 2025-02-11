import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_ENDPOINTS } from "../config";

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [game, setGame] = useState("");
  const [week, setWeek] = useState("");
  const [game_number, setGameNumber] = useState("");
  const [school, setSchool] = useState("");
  const [opponent_school, setOpponentSchool] = useState("");
  const [schools, setSchools] = useState([]); // Store fetched schools
  const [loading, setLoading] = useState(false);
  const [loadingSchools, setLoadingSchools] = useState(true); // Loading state for schools
  const navigate = useNavigate();

  // Fetch school names from the backend
  useEffect(() => {
    const fetchSchools = async () => {
      try {
        const response = await fetch(API_ENDPOINTS.handleGetSchools());
        if (!response.ok) throw new Error("Failed to fetch schools");

        const schoolList = await response.json();
        setSchools(schoolList);
      } catch (error) {
        console.error("Error fetching schools:", error);
      } finally {
        setLoadingSchools(false);
      }
    };

    fetchSchools();
  }, []);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      setFile(files[0]);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleSubmit = async () => {
    if (!file || !game || !week || !school || !game_number) {
      alert("Please fill all the fields and upload a file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("game", game);
    formData.append("week", week);
    formData.append("game_number", game_number);
    formData.append("school", school);
    formData.append("opponent_school", opponent_school);

    setLoading(true); // Start the loading animation

    try {
      const response = await fetch(API_ENDPOINTS.uploadFile, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const ocrData = await response.json();
        navigate("/modify", { state: { ocrData, file } });
      } else {
        console.error("File upload failed.");
        alert("Failed to process the file.");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("An error occurred while uploading the file.");
    } finally {
      setLoading(false); // Stop the loading animation
    }
  };

  return (
    <div className="flex h-dvh justify-center bg-custom-blue p-8">
      <div className="flex flex-col items-center">
        <h1 className="py-8 text-3xl font-semibold">Upload Game</h1>
        <div>
          <div className="mb-8 w-3/4">
            <h2 className="py-8 text-2xl font-semibold">Requirements:</h2>
            <ul className="list-disc pl-5 text-custom-off-white">
              <li>1920 x 1080 resolution</li>
              <li>16:9 aspect ratio</li>
              <li>No overlays (Discord, Outplayed, etc.)</li>
              <li>Winning Team is responsible for uploading screenshots</li>
            </ul>
          </div>
          <div className="flex justify-between rounded-md bg-custom-gray p-4 text-white">
            {/* Game Selection */}
            <select
              className="mx-2 rounded-md border border-custom-off-white bg-custom-gray py-8"
              value={game}
              onChange={(e) => setGame(e.target.value)}
            >
              <option value="">Select Game</option>
              <option value="rocket-league">Rocket League</option>
              <option value="valorant">Valorant</option>
              <option value="apex-legends">Apex Legends</option>
            </select>
            {/* Week Selection */}
            <select
              className="mx-2 rounded-md border border-custom-off-white bg-custom-gray py-8"
              value={week}
              onChange={(e) => setWeek(e.target.value)}
            >
              <option value="">Select Week</option>
              <option value="1">Week 1</option>
              <option value="2">Week 2</option>
              <option value="3">Week 3</option>
            </select>
            {/* Game Number Selection */}
            <select
              className="mx-2 rounded-md border border-custom-off-white bg-custom-gray py-8"
              value={game_number}
              onChange={(e) => setGameNumber(e.target.value)}
            >
              <option value="">Select Game Number</option>
              <option value="1">Game 1</option>
              <option value="2">Game 2</option>
              <option value="3">Game 3</option>
            </select>
            {/* Winning School Selection */}
            <select
              className="mx-2 rounded-md border border-custom-off-white bg-custom-gray py-8"
              value={school}
              onChange={(e) => setSchool(e.target.value)}
              disabled={loadingSchools}
            >
              <option value="">Select Winning School</option>
              {loadingSchools ? (
                <option>Loading...</option>
              ) : (
                schools.map((school) => (
                  <option key={school} value={school}>
                    {school}
                  </option>
                ))
              )}
            </select>
            {/* Losing School Selection */}
            {game == "valorant" && (
              <select
                className="mx-2 rounded-md border border-custom-off-white bg-custom-gray py-8"
                value={opponent_school}
                onChange={(e) => setOpponentSchool(e.target.value)}
                disabled={loadingSchools}
              >
                <option value="">Select Losing School</option>
                {loadingSchools ? (
                  <option>Loading...</option>
                ) : (
                  schools.map((school) => (
                    <option key={school} value={school}>
                      {school}
                    </option>
                  ))
                )}
              </select>
            )}
          </div>
        </div>

        {/* File Upload */}
        <div
          className="m-8 flex h-48 w-full flex-col items-center justify-center rounded-md border-2 border-dashed border-custom-off-white bg-custom-gray text-white"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {file ? (
            <p>{file.name}</p>
          ) : (
            <p>
              Drag and drop your file here or{" "}
              <label className="cursor-pointer text-custom-gold">
                browse
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </label>
            </p>
          )}

          {loading && (
            <div className="mt-8 flex flex-col items-center justify-center">
              <div className="loader h-16 w-16 animate-spin rounded-full border-t-4 border-solid border-custom-gold"></div>
              <p className="mt-4">Processing OCR...</p>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <button
          className={`m-2 bg-custom-off-white px-8 py-2 font-bold text-black transition hover:bg-custom-gold ${
            loading
              ? "cursor-not-allowed bg-gray-400"
              : "bg-blue-500 hover:bg-blue-600"
          }`}
          onClick={handleSubmit}
          disabled={loading} // Disable the button while loading
        >
          {loading ? "Processing..." : "Submit"}
        </button>
      </div>
    </div>
  );
};

export default UploadPage;
