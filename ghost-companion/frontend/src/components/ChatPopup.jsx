import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { clearSession, sendFeedback, sendMessage } from "../lib/api";
import { GhostAvatar } from "./GhostAvatar";

const initialMessages = [
  {
    id: "welcome",
    role: "boo",
    text: "Hey, main Pookie hoon 👻\nBatao, kya scene hai?",
  },
];

function Icon({ name }) {
  const paths = {
    copy: <><rect x="9" y="9" width="10" height="10" rx="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    link: <><path d="m10 13a5 5 0 0 0 7.1.1l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1" /><path d="m14 11a5 5 0 0 0-7.1-.1l-2 2A5 5 0 0 0 12 20l1.1-1.1" /></>,
    up: <path d="M7 10v10H4V10h3Zm0 10h9.2a2 2 0 0 0 1.9-1.4l1.6-5A2 2 0 0 0 17.8 11H14l.6-4.1A2.4 2.4 0 0 0 12.2 4L7 10v10Z" />,
    down: <path d="M7 14V4H4v10h3Zm0-10h9.2a2 2 0 0 1 1.9 1.4l1.6 5A2 2 0 0 1 17.8 13H14l.6 4.1a2.4 2.4 0 0 1-2.4 2.9L7 14V4Z" />,
    regenerate: <><path d="M20 11a8 8 0 0 0-14.9-4L3 10" /><path d="M3 4v6h6" /><path d="M4 13a8 8 0 0 0 14.9 4L21 14" /><path d="M21 20v-6h-6" /></>,
    more: <><circle cx="5" cy="12" r="1" fill="currentColor" /><circle cx="12" cy="12" r="1" fill="currentColor" /><circle cx="19" cy="12" r="1" fill="currentColor" /></>,
    trash: <><path d="M4 7h16" /><path d="M10 11v5M14 11v5" /><path d="M6 7l1 14h10l1-14M9 7V4h6v3" /></>,
  };
  return <svg viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>;
}

function renderMessageText(text) {
  return String(text || "").split("```").map((part, index) => {
    if (index % 2 === 0) {
      return <span key={`text-${index}`}>{part}</span>;
    }

    const hasLeadingNewline = part.startsWith("\n");
    const lines = (hasLeadingNewline ? part.slice(1) : part).split("\n");
    const hasLanguage = !hasLeadingNewline && lines.length > 1 && /^[\w+#-]+$/.test(lines[0].trim());
    const code = (hasLanguage ? lines.slice(1) : lines).join("\n").replace(/\n$/, "");

    return (
      <pre className="message-code-block" key={`code-${index}`}>
        <code>{code}</code>
      </pre>
    );
  });
}

function MessageActions({ message, precedingUserMessage, feedback, copied, moreOpen, onCopy, onFeedback, onRegenerate, onToggleMore }) {
  return (
    <div className="message-actions" aria-label="Message actions">
      <button type="button" title={copied ? "Copied" : "Copy"} aria-label={copied ? "Copied" : "Copy"} onClick={() => onCopy(message, false)}>
        <Icon name={copied ? "check" : "copy"} />
      </button>
      <button type="button" title="Copy as Markdown" aria-label="Copy as Markdown" onClick={() => onCopy(message, true)}>
        <Icon name="link" />
      </button>
      <button type="button" className={feedback === "up" ? "message-action-active" : ""} title="Thumbs up" aria-label="Thumbs up" onClick={() => onFeedback(message, precedingUserMessage, "up")}>
        <Icon name="up" />
      </button>
      <button type="button" className={feedback === "down" ? "message-action-active message-action-negative" : ""} title="Thumbs down" aria-label="Thumbs down" onClick={() => onFeedback(message, precedingUserMessage, "down")}>
        <Icon name="down" />
      </button>
      <button type="button" title="Regenerate" aria-label="Regenerate" disabled={!precedingUserMessage} onClick={() => onRegenerate(message, precedingUserMessage)}>
        <Icon name="regenerate" />
      </button>
      <span className="message-more-wrap">
        <button type="button" title="More" aria-label="More" aria-expanded={moreOpen} onClick={onToggleMore}>
          <Icon name="more" />
        </button>
        {moreOpen && (
          <div className="message-more-menu" role="menu">
            <span role="menuitem" aria-disabled="true">More actions coming soon</span>
          </div>
        )}
      </span>
    </div>
  );
}

function Message({ message, precedingUserMessage, feedback, copied, moreOpen, onCopy, onFeedback, onRegenerate, onToggleMore }) {
  return (
    <motion.div
      className={`message-row ${message.role === "user" ? "message-row-user" : "message-row-boo"}`}
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
    >
      {message.role !== "user" && <GhostAvatar mood={message.mood || "happy"} size="sm" />}
      <div className="message-content">
        <div className={`message-bubble ${message.role === "user" ? "message-bubble-user" : ""}`}>
          {renderMessageText(message.text)}
        </div>
        {message.role !== "user" && (
          <MessageActions
            message={message}
            precedingUserMessage={precedingUserMessage}
            feedback={feedback}
            copied={copied}
            moreOpen={moreOpen}
            onCopy={onCopy}
            onFeedback={onFeedback}
            onRegenerate={onRegenerate}
            onToggleMore={onToggleMore}
          />
        )}
      </div>
    </motion.div>
  );
}

export function ChatPopup({ open, mood, onMoodChange, onInteraction }) {
  const [messages, setMessages] = useState(initialMessages);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [feedbackByMessage, setFeedbackByMessage] = useState({});
  const [moreMessageId, setMoreMessageId] = useState(null);
  const [regeneratingMessageId, setRegeneratingMessageId] = useState(null);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open) window.setTimeout(() => inputRef.current?.focus(), 220);
  }, [open]);

  useEffect(() => {
    const node = scrollRef.current;
    if (node) node.scrollTop = node.scrollHeight;
  }, [messages, loading]);

  useEffect(() => {
    const unsubscribe = window.booWatcher?.onMessage?.((payload) => {
      if (!payload?.text) return;
      onMoodChange(payload.mood || "thinking");
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "boo",
          text: payload.text,
          mood: payload.mood || "thinking",
        },
      ]);
    });
    return () => unsubscribe?.();
  }, [onMoodChange]);

  async function handleSubmit(event) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || loading) return;

    setDraft("");
    setError("");
    onInteraction?.("send");
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

  async function copyMessage(message, asMarkdown = false) {
    const content = asMarkdown ? `**Pookie:**\n\n${message.text}` : message.text;
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(message.id);
      window.setTimeout(() => setCopiedMessageId((current) => (current === message.id ? null : current)), 1500);
    } catch {
      setError("Clipboard access nahi mil paaya.");
    }
  }

  async function handleFeedback(message, precedingUserMessage, rating) {
    const nextRating = feedbackByMessage[message.id] === rating ? null : rating;
    setFeedbackByMessage((current) => ({ ...current, [message.id]: nextRating }));
    if (!nextRating) return;

    try {
      await sendFeedback({
        userMessage: precedingUserMessage?.text || "",
        reply: message.text,
        rating: nextRating,
      });
    } catch (feedbackError) {
      setError(feedbackError.message);
    }
  }

  async function handleRegenerate(message, precedingUserMessage) {
    if (!precedingUserMessage || loading) return;
    setError("");
    setMoreMessageId(null);
    setLoading(true);
    setRegeneratingMessageId(message.id);
    onMoodChange("processing");

    try {
      const result = await sendMessage(precedingUserMessage.text);
      onMoodChange(result.mood || "happy");
      setMessages((current) => current.map((item) => (
        item.id === message.id
          ? { ...item, text: result.reply, mood: result.mood }
          : item
      )));
    } catch (requestError) {
      onMoodChange("concerned");
      setError(requestError.message);
    } finally {
      setLoading(false);
      setRegeneratingMessageId(null);
    }
  }

  async function handleClearChat() {
    if (!window.confirm("Clear this conversation?")) return;

    setMessages(initialMessages);
    setError("");
    setCopiedMessageId(null);
    setFeedbackByMessage({});
    setMoreMessageId(null);
    onMoodChange("happy");

    try {
      await clearSession();
    } catch (clearError) {
      setError(clearError.message);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.section
          className="chat-popup"
          aria-label="Pookie chat"
          initial={{ opacity: 0, y: 22, scale: 0.94, transformOrigin: "bottom right" }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 22, scale: 0.94 }}
          transition={{ type: "spring", stiffness: 350, damping: 28 }}
        >
          <header className="chat-header">
            <div className="chat-identity">
              <GhostAvatar mood={mood} size="sm" floating />
              <div>
                <h1>Pookie</h1>
                <p><span className="online-dot" /> Your tiny AI companion</p>
              </div>
            </div>
            <div className="chat-header-actions">
              <span className="chat-pill">{loading ? "Working…" : "Online"}</span>
              <button type="button" className="chat-header-button" title="Clear chat" aria-label="Clear chat" onClick={handleClearChat} disabled={loading}>
                <Icon name="trash" />
              </button>
            </div>
          </header>

          <div className="chat-messages" ref={scrollRef}>
            {messages.map((message, index) => {
              const precedingUserMessage = [...messages.slice(0, index)].reverse().find((item) => item.role === "user");
              return (
                <Message
                  key={message.id}
                  message={message}
                  precedingUserMessage={precedingUserMessage}
                  feedback={feedbackByMessage[message.id]}
                  copied={copiedMessageId === message.id}
                  moreOpen={moreMessageId === message.id}
                  onCopy={copyMessage}
                  onFeedback={handleFeedback}
                  onRegenerate={handleRegenerate}
                  onToggleMore={() => setMoreMessageId((current) => (current === message.id ? null : message.id))}
                />
              );
            })}
            {loading && (
              <motion.div className="message-row" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <GhostAvatar mood="processing" size="sm" />
                <div className="message-content">
                  <div className="typing-bubble"><span /><span /><span /></div>
                  {regeneratingMessageId && <span className="regenerating-label">Pookie is thinking again…</span>}
                </div>
              </motion.div>
            )}
          </div>

          <form className="chat-composer" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Type something…"
              aria-label="Message Pookie"
              disabled={loading}
            />
            <button type="submit" aria-label="Send message" disabled={!draft.trim() || loading}>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 4 16 8-16 8 3-8-3-8Zm3.2 8h7.1" /></svg>
            </button>
          </form>
          {error && <p className="chat-error">{error}</p>}
          <p className="chat-footnote">Pookie routes chats locally and tasks to your coding agent.</p>
        </motion.section>
      )}
    </AnimatePresence>
  );
}
