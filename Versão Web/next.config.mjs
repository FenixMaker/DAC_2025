/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Configuração Turbopack vazia para silenciar warning
  turbopack: {},
  webpack: (config, { isServer }) => {
    if (isServer) {
      // Ignora módulos opcionais que não estão instalados
      config.externals = [...(config.externals || []), 'mysql2/promise', 'better-sqlite3']
    }
    return config
  },
}

export default nextConfig
