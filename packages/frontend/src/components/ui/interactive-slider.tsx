'use client'

import * as React from 'react'
import * as SliderPrimitive from '@radix-ui/react-slider'
import { motion, AnimatePresence } from 'framer-motion'

import { cn } from '@/lib/utils'

function InteractiveSlider({
  className,
  defaultValue,
  value,
  min = 0,
  max = 100,
  onValueChange,
  ...props
}: React.ComponentProps<typeof SliderPrimitive.Root>) {
  const [showTooltip, setShowTooltip] = React.useState(false)
  const [internalValue, setInternalValue] = React.useState<number[]>(
    Array.isArray(value) 
      ? value 
      : Array.isArray(defaultValue) 
        ? defaultValue 
        : [min]
  )
  
  // Sync internal value if controlled value changes
  React.useEffect(() => {
    if (value !== undefined) {
      setInternalValue(value as number[])
    }
  }, [value])

  const handleValueChange = (newValue: number[]) => {
      if (value === undefined) {
          // Only update internal state directly if uncontrolled
          setInternalValue(newValue)
      }
      onValueChange?.(newValue)
  }

  return (
    <SliderPrimitive.Root
      data-slot="interactive-slider"
      defaultValue={defaultValue}
      value={value}
      min={min}
      max={max}
      onValueChange={handleValueChange}
      onPointerDown={() => setShowTooltip(true)}
      onPointerUp={() => setShowTooltip(false)}
      onBlur={() => setShowTooltip(false)}
      className={cn(
        'relative flex w-full touch-none items-center select-none data-[disabled]:opacity-50',
        className,
      )}
      {...props}
    >
      <SliderPrimitive.Track
        data-slot="slider-track"
        className="bg-muted relative grow overflow-hidden rounded-full h-3"
      >
        <SliderPrimitive.Range
          data-slot="slider-range"
          className="bg-primary absolute h-full"
        />
      </SliderPrimitive.Track>
      {internalValue.map((val, index) => (
        <SliderPrimitive.Thumb
          key={index}
          data-slot="slider-thumb"
          className="border-primary ring-ring/50 block h-6 w-6 shrink-0 rounded-full border-2 bg-white shadow-md transition-[color,box-shadow,transform] hover:scale-110 focus-visible:ring-4 focus-visible:outline-hidden disabled:pointer-events-none disabled:opacity-50"
        >
             <AnimatePresence>
                {showTooltip && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.8 }}
                        animate={{ opacity: 1, y: -35, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.8 }}
                        transition={{ duration: 0.15 }}
                        className="absolute -top-1 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-xs font-bold px-2 py-1 rounded-md whitespace-nowrap z-50 pointer-events-none tabular-nums shadow-sm"
                    >
                        {val}
                        <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 border-4 border-transparent border-t-primary" />
                    </motion.div>
                )}
            </AnimatePresence>
        </SliderPrimitive.Thumb>
      ))}
    </SliderPrimitive.Root>
  )
}

export { InteractiveSlider }

