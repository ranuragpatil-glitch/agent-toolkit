import { motion } from "framer-motion";

const moodAsset = (name) => `${import.meta.env.BASE_URL}assets/moods/${name}.png`;

const MOODS = {
  happy: { src: moodAsset("happy"), label: "Happy" },
  thinking: { src: moodAsset("thinking"), label: "Thinking" },
  concerned: { src: moodAsset("concerned"), label: "Concerned" },
  proud: { src: moodAsset("proud"), label: "Proud" },
  processing: { src: moodAsset("processing"), label: "Processing" },
  angry: { src: moodAsset("angry"), label: "Frustrated" },
  sulking: { src: moodAsset("sulking"), label: "Sulking" },
  notification: { src: moodAsset("notification"), label: "Notification" },
};

export function GhostAvatar({ mood = "happy", size = "md", floating = false }) {
  const selected = MOODS[mood] || MOODS.happy;
  const sizeClass = size === "lg" ? "ghost-avatar-lg" : size === "sm" ? "ghost-avatar-sm" : "ghost-avatar-md";

  return (
    <motion.div
      className={`ghost-avatar ${sizeClass} ${floating ? "ghost-avatar-floating" : ""}`}
      animate={floating ? { y: [0, -5, 0], rotate: [0, 1.5, 0] } : undefined}
      transition={floating ? { duration: 4.5, repeat: Infinity, ease: "easeInOut" } : undefined}
      title={`Boo is ${selected.label.toLowerCase()}`}
    >
      <img src={selected.src} alt={`Boo — ${selected.label}`} />
    </motion.div>
  );
}

export { MOODS };
