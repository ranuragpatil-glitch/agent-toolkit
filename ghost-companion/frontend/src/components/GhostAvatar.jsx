import { motion } from "framer-motion";
import { useEffect, useState } from "react";

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
  const [blinking, setBlinking] = useState(false);

  useEffect(() => {
    if (!floating) return undefined;

    let blinkTimer;
    let openEyesTimer;
    let stopped = false;

    const scheduleBlink = () => {
      blinkTimer = window.setTimeout(() => {
        if (stopped) return;
        setBlinking(true);
        openEyesTimer = window.setTimeout(() => {
          setBlinking(false);
          scheduleBlink();
        }, 160);
      }, 4000 + Math.random() * 4000);
    };

    scheduleBlink();
    return () => {
      stopped = true;
      window.clearTimeout(blinkTimer);
      window.clearTimeout(openEyesTimer);
    };
  }, [floating]);

  return (
    <motion.div
      className={`ghost-avatar ${sizeClass} ${floating ? "ghost-avatar-floating" : ""} ${blinking ? "ghost-avatar-blinking" : ""}`}
      title={`Pookie is ${selected.label.toLowerCase()}`}
    >
      <img src={selected.src} alt={`Pookie — ${selected.label}`} />
      {blinking && <><span className="ghost-blink-eye ghost-blink-eye-left" /><span className="ghost-blink-eye ghost-blink-eye-right" /></>}
    </motion.div>
  );
}

export { MOODS };
