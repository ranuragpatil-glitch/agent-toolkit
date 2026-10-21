import { AnimatePresence, motion } from "framer-motion";
import { GhostAvatar } from "./GhostAvatar";

export function CompanionButton({ open, mood, moment, onClick, onInteraction }) {
  return (
    <motion.button
      type="button"
      className={`companion-button ${moment ? `companion-button-${moment.kind}` : ""}`}
      aria-label={open ? "Close Pookie chat" : "Open Pookie chat"}
      onPointerDown={() => onInteraction?.("pointer")}
      onClick={onClick}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.96 }}
    >
      <span className="companion-glow" />
      {moment && <span className="companion-speech-bubble" role="status">{moment.text}</span>}
      <GhostAvatar mood={mood} size="sm" floating />
      <AnimatePresence initial={false} mode="wait">
        <motion.span
          key={open ? "close" : "open"}
          className="companion-label"
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          transition={{ duration: 0.16 }}
        >
          {open ? "Close" : "Talk to Pookie"}
        </motion.span>
      </AnimatePresence>
      <span className="status-dot" />
    </motion.button>
  );
}
