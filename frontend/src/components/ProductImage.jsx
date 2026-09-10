import React from 'react'

export default function ProductImage({ src, alt, className = '' }) {
  const [failed, setFailed] = React.useState(false)

  if (!src || failed) {
    return (
      <div className={`flex items-center justify-center bg-slate-100 text-4xl ${className}`}>
        📦
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      onError={() => setFailed(true)}
      loading="lazy"
    />
  )
}
