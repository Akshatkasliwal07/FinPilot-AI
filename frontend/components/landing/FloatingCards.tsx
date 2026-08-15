"use client";

import { motion } from "framer-motion";
import FloatingStat from "./FloatingStat";

export default function FloatingCards() {
  return (
    <>
      <motion.div
        animate={{ y: [0, -10, 0] }}
        transition={{
          repeat: Infinity,
          duration: 4,
        }}
        className="absolute -left-12 top-10 w-48"
      >
        <FloatingStat
          title="AI Accuracy"
          value="99.8%"
          color="text-cyan-400"
        />
      </motion.div>

      <motion.div
        animate={{ y: [0, 10, 0] }}
        transition={{
          repeat: Infinity,
          duration: 5,
        }}
        className="absolute -right-10 bottom-12 w-52"
      >
        <FloatingStat
          title="Today's Profit"
          value="+$2,540"
          color="text-green-400"
        />
      </motion.div>
    </>
  );
}