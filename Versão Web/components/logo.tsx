import Image from "next/image"

type LogoVariant = "simplified" | "color" | "mono-black" | "mono-white"

const VARIANT_SRC: Record<LogoVariant, { png: string; svg: string }> = {
  simplified: { png: "/logos/dac-simplified.png", svg: "/logos/dac-simplified.svg" },
  color: { png: "/logos/dac-color.png", svg: "/logos/dac-color.svg" },
  "mono-black": { png: "/logos/dac-mono-black.png", svg: "/logos/dac-mono-black.svg" },
  "mono-white": { png: "/logos/dac-mono-white.png", svg: "/logos/dac-mono-white.svg" },
}

export function Logo({
  variant = "simplified",
  size = 40,
  className = "",
  priority = false,
}: {
  variant?: LogoVariant
  size?: number
  className?: string
  priority?: boolean
}) {
  // Preferir PNG conforme solicitação do usuário; SVG permanece disponível nos assets
  const src = VARIANT_SRC[variant].png
  return (
    <Image
      src={src}
      alt={`Logo DAC (${variant})`}
      width={size}
      height={size}
      sizes={`${size}px`}
      className={`object-cover ${className}`}
      priority={priority}
    />
  )
}
