"use client"

import { useAnimation, AnimationControls } from "framer-motion"
import { useEffect, useRef } from "react"

export function useRefreshAnimation(value: any, duration = 0.3): AnimationControls {
  const controls = useAnimation()
  const isFirstRender = useRef(true)

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false
      return
    }

    controls.start({
      scale: [1, 1.05, 1],
      backgroundColor: ["rgba(var(--primary), 0)", "rgba(var(--primary), 0.1)", "rgba(var(--primary), 0)"],
      transition: { duration }
    })
  }, [value, controls, duration])

  return controls
}
