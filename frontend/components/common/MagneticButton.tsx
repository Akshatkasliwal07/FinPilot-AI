"use client";

import { motion } from "framer-motion";

export default function MagneticButton({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <motion.button
      whileHover={{
        scale: 1.05,
        y: -3,
      }}
      whileTap={{
        scale: 0.95,
      }}
      className="rounded-2xl bg-blue-600 px-6 py-3 font-semibold"
    >
      {children}
    </motion.button>
  );
}