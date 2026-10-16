import { AnimatePresence, motion } from "framer-motion";
import { GhostAvatar } from "./GhostAvatar";

export function CompanionButton({ open, mood, onClick }) {
  return (
    <motion.button
      type="button"
      className="companion-button"
      aria-label={open ? "Close Boo chat" : "Open Boo chat"}
      onClick={onClick}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.96 }}
    >
      <span className="companion-glow" />
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
          {open ? "Close" : "Talk to Boo"}
        </motion.span>
      </AnimatePresence>
      <span className="status-dot" />
    </motion.button>
  );
}
