import { useCallback, useEffect, useRef, useState } from "react";
import { CompanionButton } from "./components/CompanionButton";
import { ChatPopup } from "./components/ChatPopup";
import { NEGLECT_PHRASES, WELCOME_BACK_PHRASES } from "./data/companionPhrases";

const IDLE_CHECK_MS = 1000;
const NEUTRAL_AFTER_MS = 5 * 60 * 1000;
const SAD_AFTER_MS = 20 * 60 * 1000;
const ATTENTION_EVERY_MS = 2 * 60 * 1000;
const MOMENT_VISIBLE_MS = 3500;
// Set VITE_IDLE_TIMER_SCALE only for local testing; production defaults to 1.
const TIMER_SCALE = Math.max(0.001, Number(import.meta.env.VITE_IDLE_TIMER_SCALE || 1));

const pickRandom = (items) => items[Math.floor(Math.random() * items.length)];

function idleMoodFor(stage) {
  if (stage === "sad") return "sulking";
  if (stage === "neutral") return "thinking";
  return "happy";
}

function App() {
  const [open, setOpen] = useState(false);
  const [mood, setMood] = useState("happy");
  const [lastInteractionAt, setLastInteractionAt] = useState(() => Date.now());
  const [clock, setClock] = useState(() => Date.now());
  const [moment, setMoment] = useState(null);
  const momentTimerRef = useRef(null);
  const nextAttentionAtRef = useRef(null);
  const sadInteractionPendingRef = useRef(false);

  const elapsed = clock - lastInteractionAt;
  const idleStage = elapsed >= SAD_AFTER_MS * TIMER_SCALE
    ? "sad"
    : elapsed >= NEUTRAL_AFTER_MS * TIMER_SCALE
      ? "neutral"
      : "happy";

  useEffect(() => {
    const timer = window.setInterval(() => setClock(Date.now()), IDLE_CHECK_MS);
    return () => window.clearInterval(timer);
  }, []);

  const showMoment = useCallback((kind, text) => {
    window.clearTimeout(momentTimerRef.current);
    setMoment({ kind, text });
    momentTimerRef.current = window.setTimeout(() => setMoment(null), MOMENT_VISIBLE_MS);
  }, []);

  const clearMoment = useCallback(() => {
    window.clearTimeout(momentTimerRef.current);
    momentTimerRef.current = null;
    setMoment(null);
  }, []);

  useEffect(() => () => window.clearTimeout(momentTimerRef.current), []);

  useEffect(() => {
    if (idleStage !== "sad" || open) {
      nextAttentionAtRef.current = null;
      return;
    }

    if (nextAttentionAtRef.current === null) {
      nextAttentionAtRef.current = clock + Math.max(2500, ATTENTION_EVERY_MS * TIMER_SCALE);
    }

    if (clock >= nextAttentionAtRef.current && !moment) {
      showMoment("attention", pickRandom(NEGLECT_PHRASES));
      nextAttentionAtRef.current = clock + Math.max(2500, ATTENTION_EVERY_MS * TIMER_SCALE);
    }
  }, [clock, idleStage, moment, open, showMoment]);

  const recordInteraction = useCallback((type) => {
    const wasSad = idleStage === "sad" || sadInteractionPendingRef.current;
    if (type === "pointer") {
      sadInteractionPendingRef.current = idleStage === "sad";
    } else {
      sadInteractionPendingRef.current = false;
    }
    const now = Date.now();
    setLastInteractionAt(now);
    setClock(now);
    nextAttentionAtRef.current = null;
    clearMoment();

    if (wasSad && (type === "open" || type === "send")) {
      setMood("happy");
      showMoment("celebration", pickRandom(WELCOME_BACK_PHRASES));
    }
  }, [clearMoment, idleStage, showMoment]);

  function handleCompanionClick() {
    const nextOpen = !open;
    recordInteraction(nextOpen ? "open" : "close");
    setOpen(nextOpen);
  }

  const companionMood = open ? mood : idleMoodFor(idleStage);

  return (
    <main className={`app-shell ${open ? "chat-open" : ""}`}>
      <ChatPopup open={open} mood={mood} onMoodChange={setMood} onInteraction={recordInteraction} />
      <CompanionButton
        open={open}
        mood={companionMood}
        moment={moment}
        onInteraction={recordInteraction}
        onClick={handleCompanionClick}
      />
    </main>
  );
}

export default App;
