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
    throw new Error("Boo backend ne readable response nahi diya.");
  }

  if (!response.ok) {
    throw new Error(data?.detail || "Boo backend se connection fail ho gaya.");
  }
  return data;
}
