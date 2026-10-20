import { motion } from "framer-motion";

const MOOD_EMOJI = {
  happy: "😊",
  thinking: "🤔",
  concerned: "😟",
  proud: "😎",
  processing: "🛠️",
  angry: "😠",
  sulking: "😒",
  notification: "🔔",
};

const MOOD_COLOR = {
  happy: "#a78bfa",
  thinking: "#93c5fd",
  concerned: "#fca5a5",
  proud: "#86efac",
  processing: "#fcd34d",
  angry: "#f87171",
  sulking: "#c4b5fd",
  notification: "#67e8f9",
};

export function GhostAvatar({ mood = "happy", size = "md", floating = false }) {
  const emoji = MOOD_EMOJI[mood] || "👻";
  const color = MOOD_COLOR[mood] || "#a78bfa";

  const sizeMap = {
    sm: 36,
    md: 56,
    lg: 80,
  };
  const px = sizeMap[size] || 56;

  return (
    <motion.div
      className="ghost-avatar"
      style={{
        width: px,
        height: px,
        background: `linear-gradient(135deg, ${color}, #7c3aed)`,
        borderRadius: "50%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: px * 0.5,
        boxShadow: `0 4px 20px ${color}55`,
        flexShrink: 0,
      }}
      animate={
        floating
          ? { y: [0, -6, 0], rotate: [0, 3, -3, 0] }
          : { scale: [1, 1.05, 1] }
      }
      transition={
        floating
          ? { duration: 3.5, repeat: Infinity, ease: "easeInOut" }
          : { duration: 0.3 }
      }
      title={`Pookie is ${mood}`}
    >
      {emoji}
    </motion.div>
  );
}
