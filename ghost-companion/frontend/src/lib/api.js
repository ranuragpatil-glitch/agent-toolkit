const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function sendMessage(message) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("Pookie backend ne readable response nahi diya.");
  }

  if (!response.ok) {
    throw new Error(data?.detail || "Pookie backend se connection fail ho gaya.");
  }
  return data;
}

export async function sendFeedback({ userMessage, reply, rating }) {
  const response = await fetch(`${API_URL}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_message: userMessage, reply, rating }),
  });

  if (!response.ok) {
    let data;
    try {
      data = await response.json();
    } catch {
      data = null;
    }
    throw new Error(data?.detail || "Feedback save nahi ho paaya.");
  }
  return response.json();
}

export async function clearSession() {
  const response = await fetch(`${API_URL}/session/clear`, { method: "POST" });
  if (!response.ok) {
    throw new Error("Pookie ki conversation memory reset nahi ho paayi.");
  }
  return response.json();
}
