const API_BASE_URL = "http://localhost:8080";

const API_ENDPOINTS = {
  getPlayerStats: (videogame, playerName) =>
    `${API_BASE_URL}/player/${videogame}?player=${encodeURIComponent(playerName)}`,
  getGameReports: (videogame, week) =>
    `${API_BASE_URL}/stats/${videogame}?week=${encodeURIComponent(week)}`,
  uploadFile: `${API_BASE_URL}/upload_file`,
  uploadMatch: `${API_BASE_URL}/upload_match`,
  getAllDisputes: `${API_BASE_URL}/get_all_disputes`,
  resolveDispute: (gameId) => `${API_BASE_URL}/resolve_dispute/${gameId}`,
  handleLogin: () => `${API_BASE_URL}/login`,
  handleGetAccounts: () => `${API_BASE_URL}/accounts`,
  handleCreateAccount: () => `${API_BASE_URL}/accounts`,
  handleChangePassword: () => `${API_BASE_URL}/accounts`,
  handleDeleteAccount: () => `${API_BASE_URL}/accounts`,
  handleSubmitRoster: (videogame) => `${API_BASE_URL}/roster/${videogame}`,
  handleGetRoster: (videogame, school) =>
    `${API_BASE_URL}/roster/${videogame}?school=${encodeURIComponent(school)}`,
  handleDeleteRoster: (videogame) => `${API_BASE_URL}/roster/${videogame}`,
  handleGetSchools: () => `${API_BASE_URL}/schools`,
};

export { API_BASE_URL, API_ENDPOINTS };
