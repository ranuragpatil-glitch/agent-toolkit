import { useState } from "react";
import { CompanionButton } from "./components/CompanionButton";
import { ChatPopup } from "./components/ChatPopup";

function App() {
  const [open, setOpen] = useState(false);
  const [mood, setMood] = useState("happy");

  return (
    <main className={`app-shell ${open ? "chat-open" : ""}`}>
      <ChatPopup open={open} mood={mood} onMoodChange={setMood} />
      <CompanionButton open={open} mood={mood} onClick={() => setOpen((current) => !current)} />
    </main>
  );
}

export default App;
