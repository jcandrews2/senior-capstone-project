const API_BASE_URL = "http://127.0.0.1:8080";

const API_ENDPOINTS = {
  getPlayerStats: (game, playerName) =>
    `${API_BASE_URL}/player/${game}?player=${encodeURIComponent(playerName)}`,
  getGameReports: (game, week) => `${API_BASE_URL}/stats/${game}/${week}`,
  uploadFile: `${API_BASE_URL}/upload_file`,
  uploadMatch: `${API_BASE_URL}/upload_match`,
  getAllDisputes: `${API_BASE_URL}/get_all_disputes`,
  resolveDispute: (gameId) => `${API_BASE_URL}/resolve_dispute/${gameId}`,
};

export { API_BASE_URL, API_ENDPOINTS };
