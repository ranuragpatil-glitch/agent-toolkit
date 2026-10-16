import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { sendMessage } from "../lib/api";
import { GhostAvatar } from "./GhostAvatar";

const initialMessages = [
  {
    id: "welcome",
    role: "boo",
    text: "Hey, main Boo hoon 👻\nBatao, kya scene hai?",
  },
];

function Message({ message }) {
  return (
    <motion.div
      className={`message-row ${message.role === "user" ? "message-row-user" : ""}`}
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
    >
      {message.role !== "user" && <GhostAvatar mood={message.mood || "happy"} size="sm" />}
      <div className={`message-bubble ${message.role === "user" ? "message-bubble-user" : ""}`}>
        {message.text}
      </div>
    </motion.div>
  );
}

export function ChatPopup({ open, mood, onMoodChange }) {
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open) window.setTimeout(() => inputRef.current?.focus(), 220);
  }, [open]);

  useEffect(() => {
    const node = scrollRef.current;
    if (node) node.scrollTop = node.scrollHeight;
  }, [messages, loading]);

  async function handleSubmit(event) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || loading) return;

    setDraft("");
    setError("");
    setMessages((current) => [...current, { id: crypto.randomUUID(), role: "user", text: message }]);
    setLoading(true);
    onMoodChange("processing");

    try {
      const result = await sendMessage(message);
      onMoodChange(result.mood || "happy");
      setMessages((current) => [
        ...current,
        { id: crypto.randomUUID(), role: "boo", text: result.reply, mood: result.mood },
      ]);
    } catch (requestError) {
      onMoodChange("concerned");
      setError(requestError.message);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "boo",
          text: "Oops, connection mein thoda bhoot aa gaya 😵 Backend check kar lo.",
          mood: "concerned",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.section
          className="chat-popup"
          aria-label="Boo chat"
          initial={{ opacity: 0, y: 22, scale: 0.94, transformOrigin: "bottom right" }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 22, scale: 0.94 }}
          transition={{ type: "spring", stiffness: 350, damping: 28 }}
        >
          <header className="chat-header">
            <div className="chat-identity">
              <GhostAvatar mood={mood} size="sm" floating />
              <div>
                <h1>Boo</h1>
                <p><span className="online-dot" /> Your tiny AI companion</p>
              </div>
            </div>
            <span className="chat-pill">{loading ? "Working…" : "Online"}</span>
          </header>

          <div className="chat-messages" ref={scrollRef}>
            {messages.map((message) => <Message key={message.id} message={message} />)}
            {loading && (
              <motion.div className="message-row" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <GhostAvatar mood="processing" size="sm" />
                <div className="typing-bubble"><span /><span /><span /></div>
              </motion.div>
            )}
          </div>

          <form className="chat-composer" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Type something…"
              aria-label="Message Boo"
              disabled={loading}
            />
            <button type="submit" aria-label="Send message" disabled={!draft.trim() || loading}>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 4 16 8-16 8 3-8-3-8Zm3.2 8h7.1" /></svg>
            </button>
          </form>
          {error && <p className="chat-error">{error}</p>}
          <p className="chat-footnote">Boo routes chats locally and tasks to your coding agent.</p>
        </motion.section>
      )}
    </AnimatePresence>
  );
}
