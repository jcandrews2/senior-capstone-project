const API_BASE_URL = "http://40.85.147.30:8080";

const API_ENDPOINTS = {
  getPlayerStats: (videogame, playerName) =>
    `${API_BASE_URL}/player/${videogame}?player=${encodeURIComponent(playerName)}`,
  getGameReports: (videogame, week) => `${API_BASE_URL}/stats/${videogame}?week=${encodeURIComponent(week)}`,
  uploadFile: `${API_BASE_URL}/upload_file`,
  uploadMatch: `${API_BASE_URL}/upload_match`,
  getAllDisputes: `${API_BASE_URL}/get_all_disputes`,
  resolveDispute: (gameId) => `${API_BASE_URL}/resolve_dispute/${gameId}`,
};

export { API_BASE_URL, API_ENDPOINTS };
