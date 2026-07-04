import { useState, useEffect } from "react";

// ─── Hide and Seek Landing Page ────────────────────────────────────────
// Documentation/download page for the Python desktop app (Hide and Seek.py)

export default function App() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandCode, setExpandCode] = useState(false);

  const isDark = theme === "dark";
  const toggleTheme = () => setTheme(t => t === "dark" ? "light" : "dark");

  // Scroll animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("opacity-100", "translate-y-0");
            entry.target.classList.remove("opacity-0", "translate-y-4");
          }
        });
      },
      { threshold: 0.1 }
    );
    document.querySelectorAll(".fade-up").forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [theme]);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Theme colors
  const bg = isDark ? "bg-[#0d1117]" : "bg-white";
  const bgAlt = isDark ? "bg-[#161b22]" : "bg-[#f6f8fa]";
  const card = isDark ? "bg-[#161b22]" : "bg-white";
  const border = isDark ? "border-[#30363d]" : "border-[#d0d7de]";
  const text = isDark ? "text-[#f0f6fc]" : "text-[#1f2328]";
  const textSec = isDark ? "text-[#8b949e]" : "text-[#656d76]";
  const textMuted = isDark ? "text-[#6e7681]" : "text-[#8c959f]";

  return (
    <div className={`min-h-screen ${bg} ${text} transition-colors duration-300`}>
      {/* ── Navbar ── */}
      <nav className={`sticky top-0 z-50 ${isDark ? "bg-[#161b22]/95" : "bg-white/95"} backdrop-blur-xl border-b ${border}`}>
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xl shadow-lg">
              🔐
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight">Hide and Seek</span>
              <span className={`text-xs ${textMuted} ml-2 hidden sm:inline`}>v1.0</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <a href="#features" className={`text-sm ${textSec} ${isDark ? "hover:text-[#f0f6fc]" : "hover:text-[#1f2328]"} transition-colors hidden sm:inline`}>Features</a>
            <a href="#install" className={`text-sm ${textSec} ${isDark ? "hover:text-[#f0f6fc]" : "hover:text-[#1f2328]"} transition-colors hidden sm:inline`}>Install</a>
            <a href="#how" className={`text-sm ${textSec} ${isDark ? "hover:text-[#f0f6fc]" : "hover:text-[#1f2328]"} transition-colors hidden sm:inline`}>How it works</a>
            <button
              onClick={toggleTheme}
              aria-label={isDark ? "Switch to light theme" : "Switch to dark theme"}
              className={`w-10 h-10 rounded-xl ${isDark ? "bg-[#21262d] hover:bg-[#30363d]" : "bg-[#f6f8fa] hover:bg-[#eaeef2]"} flex items-center justify-center transition-all text-lg`}
            >
              {isDark ? "☀️" : "🌙"}
            </button>
          </div>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative overflow-hidden">
        <div className={`absolute inset-0 ${isDark ? "bg-gradient-to-b from-[#0d1117] via-[#0d1117] to-[#161b22]" : "bg-gradient-to-b from-white via-white to-[#f6f8fa]"}`} />
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className={`absolute -top-32 -right-32 w-[500px] h-[500px] rounded-full ${isDark ? "bg-blue-500/5" : "bg-blue-500/10"} blur-[100px]`} />
          <div className={`absolute -bottom-32 -left-32 w-[500px] h-[500px] rounded-full ${isDark ? "bg-purple-500/5" : "bg-purple-500/10"} blur-[100px]`} />
        </div>

        <div className="relative max-w-5xl mx-auto px-6 py-24 text-center">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border ${border} ${bgAlt} mb-8 text-sm ${textSec}`}>
            <span className="w-2 h-2 rounded-full bg-[#3fb950] animate-pulse" />
            Python Desktop Application • Open Source
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight mb-6 leading-[1.1]">
            Hide secrets in
            <br />
            <span className={`bg-gradient-to-r ${isDark ? "from-[#58a6ff] via-[#bc8cff] to-[#f778ba]" : "from-[#0969da] via-[#8250df] to-[#bf3989]"} bg-clip-text text-transparent`}>
              plain sight
            </span>
          </h1>

          <p className={`text-lg sm:text-xl ${textSec} max-w-2xl mx-auto mb-10 leading-relaxed`}>
            A modern Python desktop application for image steganography.
            Hide encrypted messages inside images using the LSB technique — 
            completely invisible to the human eye.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={() => handleCopy("quickstart", "pip install customtkinter Pillow cryptography numpy && python Hide and Seek.py")}
              aria-label="Copy quick start command to clipboard"
              className={`px-8 py-4 rounded-xl font-semibold text-white ${isDark ? "bg-[#238636] hover:bg-[#2ea043]" : "bg-[#1a7f37] hover:bg-[#116329]"} transition-all hover:scale-[1.02] active:scale-[0.98] shadow-xl shadow-green-500/20 flex items-center gap-2`}
            >
              {copiedId === "quickstart" ? "✅ Copied to clipboard!" : "📋 Copy Quick Start Command"}
            </button>
            <a
              href="#install"
              className={`px-8 py-4 rounded-xl font-semibold border ${border} ${isDark ? "hover:bg-[#21262d]" : "hover:bg-[#f6f8fa]"} transition-all flex items-center gap-2`}
            >
              View Instructions
              <span className="text-sm">↓</span>
            </a>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" className={`${bgAlt} border-t border-b ${border} py-24`}>
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16 fade-up opacity-0 translate-y-4 transition-all duration-700">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Everything you need</h2>
            <p className={`${textSec} text-lg max-w-xl mx-auto`}>
              Professional steganography features in a beautiful, easy-to-use interface
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: "🔒", title: "LSB Encoding", desc: "Hides in the least significant bits of RGB pixels — completely invisible" },
              { icon: "🔓", title: "Smart Decoding", desc: "Extract hidden data with magic header verification (STEG) for reliable detection" },
              { icon: "🔑", title: "AES-256 Encryption", desc: "Optional Fernet encryption with PBKDF2 key derivation (100,000 iterations)" },
              { icon: "🎨", title: "Modern UI", desc: "GitHub-inspired dark/light theme with smooth animations and clean design" },
              { icon: "📊", title: "Image Comparison", desc: "Side-by-side view with amplified difference map and PSNR calculation" },
              { icon: "🛡️", title: "Risk Meter", desc: "Real-time detection risk analysis with LOW/MEDIUM/HIGH indicators" },
              { icon: "🌍", title: "Unicode Support", desc: "Full support for international text including Arabic, Persian, Chinese, and emoji" },
              { icon: "📁", title: "Multi-Format", desc: "Supports PNG, BMP, TIFF, WebP input — always outputs lossless PNG" },
              { icon: "✨", title: "Animations", desc: "Smooth progress bars, color pulses, and typewriter effects for a polished feel" },
            ].map((f, i) => (
              <div
                key={i}
                className={`fade-up opacity-0 translate-y-4 transition-all duration-500 ${card} rounded-2xl border ${border} p-6 ${isDark ? "hover:border-[#484f58]" : "hover:border-[#afb8c1]"} hover:shadow-xl group`}
                style={{ transitionDelay: `${i * 50}ms` }}
              >
                <div className="text-3xl mb-4 group-hover:scale-110 transition-transform">{f.icon}</div>
                <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
                <p className={`text-sm ${textSec} leading-relaxed`}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="how" className="py-24">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16 fade-up opacity-0 translate-y-4 transition-all duration-700">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">How it works</h2>
            <p className={`${textSec} text-lg`}>LSB Steganography in 4 simple steps</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-16">
            {[
              { step: "01", title: "Select Image", desc: "Choose a PNG, BMP, TIFF, or WebP carrier image", color: isDark ? "#58a6ff" : "#0969da" },
              { step: "02", title: "Enter Message", desc: "Type your secret text and optionally set a password", color: isDark ? "#3fb950" : "#1a7f37" },
              { step: "03", title: "Hide Data", desc: "Each bit replaces the LSB of R, G, B color channels", color: isDark ? "#d29922" : "#9a6700" },
              { step: "04", title: "Save & Share", desc: "Output PNG looks identical — the message is invisible", color: isDark ? "#bc8cff" : "#8250df" },
            ].map((s, i) => (
              <div key={i} className="text-center relative fade-up opacity-0 translate-y-4 transition-all duration-500" style={{ transitionDelay: `${i * 100}ms` }}>
                <div
                  className="w-16 h-16 rounded-2xl mx-auto mb-5 flex items-center justify-center text-xl font-bold shadow-lg"
                  style={{ backgroundColor: s.color + "20", color: s.color, boxShadow: `0 8px 32px ${s.color}20` }}
                >
                  {s.step}
                </div>
                <h3 className="font-semibold text-lg mb-2">{s.title}</h3>
                <p className={`text-sm ${textSec}`}>{s.desc}</p>
                {i < 3 && (
                  <div className={`hidden md:block absolute top-8 -right-4 text-2xl ${textMuted}`}>→</div>
                )}
              </div>
            ))}
          </div>

          {/* Protocol diagram */}
          <div className={`fade-up opacity-0 translate-y-4 transition-all duration-700 ${card} rounded-2xl border ${border} p-8 max-w-4xl mx-auto`}>
            <h3 className="font-semibold text-lg mb-6 flex items-center gap-3">
              <span className="text-2xl">📐</span>
              Binary Protocol Layout
            </h3>
            <div className="overflow-x-auto">
              <div className="flex gap-2 min-w-[700px]">
                {[
                  { label: "MAGIC", bits: "32 bits", desc: '"STEG"', color: isDark ? "#58a6ff" : "#0969da" },
                  { label: "FLAG", bits: "8 bits", desc: "Encrypt?", color: isDark ? "#d29922" : "#9a6700" },
                  { label: "SALT", bits: "128 bits", desc: "Per-message", color: isDark ? "#3fb950" : "#1a7f37" },
                  { label: "LENGTH", bits: "32 bits", desc: "Size", color: isDark ? "#d29922" : "#9a6700" },
                  { label: "PAYLOAD", bits: "N bits", desc: "Message", color: isDark ? "#bc8cff" : "#8250df", grow: true },
                ].map((block, i) => (
                  <div
                    key={i}
                    className={`${block.grow ? "flex-[2]" : "flex-1"} rounded-xl p-4 text-center transition-all hover:scale-[1.02]`}
                    style={{ backgroundColor: block.color + "15", borderLeft: `4px solid ${block.color}` }}
                  >
                    <div className="font-bold text-sm" style={{ color: block.color }}>{block.label}</div>
                    <div className={`text-xs ${textMuted} mt-1`}>{block.bits}</div>
                    <div className={`text-xs ${textSec} mt-1`}>{block.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Installation ── */}
      <section id="install" className={`${bgAlt} border-t border-b ${border} py-24`}>
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-12 fade-up opacity-0 translate-y-4 transition-all duration-700">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Get Started</h2>
            <p className={`${textSec} text-lg`}>Up and running in seconds</p>
          </div>

          <div className="space-y-5">
            {/* Step 1 */}
            <div className={`fade-up opacity-0 translate-y-4 transition-all duration-500 ${card} rounded-2xl border ${border} overflow-hidden`}>
              <div className={`px-6 py-4 ${isDark ? "bg-[#21262d]" : "bg-[#f6f8fa]"} border-b ${border} flex items-center gap-4`}>
                <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${isDark ? "bg-[#58a6ff]/20 text-[#58a6ff]" : "bg-[#0969da]/20 text-[#0969da]"}`}>1</span>
                <span className="font-medium">Install dependencies</span>
              </div>
              <div className="p-6">
                <div className={`${isDark ? "bg-[#0d1117]" : "bg-[#f6f8fa]"} rounded-xl p-4 font-mono text-sm relative group border ${border}`}>
                  <code className={isDark ? "text-[#58a6ff]" : "text-[#0969da]"}>pip install customtkinter Pillow cryptography numpy</code>
                  <button
                    onClick={() => handleCopy("pip-install", "pip install customtkinter Pillow cryptography numpy")}
                    aria-label="Copy pip install command"
                    className={`absolute top-3 right-3 px-3 py-1.5 rounded-lg text-xs font-medium ${isDark ? "bg-[#30363d] hover:bg-[#484f58]" : "bg-[#eaeef2] hover:bg-[#d0d7de]"} opacity-0 group-hover:opacity-100 transition-all`}
                  >
                    {copiedId === "pip-install" ? "✅" : "Copy"}
                  </button>
                </div>
              </div>
            </div>

            {/* Step 2 */}
            <div className={`fade-up opacity-0 translate-y-4 transition-all duration-500 ${card} rounded-2xl border ${border} overflow-hidden`} style={{ transitionDelay: "100ms" }}>
              <div className={`px-6 py-4 ${isDark ? "bg-[#21262d]" : "bg-[#f6f8fa]"} border-b ${border} flex items-center gap-4`}>
                <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${isDark ? "bg-[#3fb950]/20 text-[#3fb950]" : "bg-[#1a7f37]/20 text-[#1a7f37]"}`}>2</span>
                <span className="font-medium">Download the application</span>
              </div>
              <div className="p-6">
                <p className={`text-sm ${textSec} mb-4`}>
                  Save <code className={`${isDark ? "bg-[#30363d]" : "bg-[#eaeef2]"} px-2 py-1 rounded text-sm font-mono`}>Hide and Seek.py</code> (single file, ~1600 lines)
                </p>
                <button
                  onClick={() => setExpandCode(!expandCode)}
                  className={`text-sm font-medium ${isDark ? "text-[#58a6ff] hover:text-[#79c0ff]" : "text-[#0969da] hover:text-[#0550ae]"} transition-colors`}
                >
                  {expandCode ? "Hide code preview ▲" : "Show code preview ▼"}
                </button>
                {expandCode && (
                  <div className={`mt-4 ${isDark ? "bg-[#0d1117]" : "bg-[#f6f8fa]"} rounded-xl p-4 font-mono text-xs max-h-64 overflow-y-auto border ${border}`}>
                    <pre className="whitespace-pre-wrap text-[#8b949e]">
{`#!/usr/bin/env python3
"""
Hide and Seek v1.0 - Image Steganography Application

Key Components:
  • Steganography class - LSB encode/decode with AES encryption
  • SteganoApp class - CustomTkinter GUI with GitHub-inspired theme  
  • Animator class - Smooth animations (progress, pulse, typewriter)
  • Theme class - Dark/Light color palettes

Features:
  ✓ LSB steganography (RGB channels)
  ✓ STEG magic header verification
  ✓ AES-256 encryption via Fernet + PBKDF2
  ✓ Dark/Light theme toggle
  ✓ Image comparison with PSNR
  ✓ Detection risk meter
  ✓ Unicode text support (including Farsi/Persian)
  ✓ Cross-platform (Windows, macOS, Linux)

Full source: Hide and Seek.py in project root
"""

# The complete 1600+ line application is available
# in the Hide and Seek.py file. Run with:
#   python Hide and Seek.py`}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {/* Step 3 */}
            <div className={`fade-up opacity-0 translate-y-4 transition-all duration-500 ${card} rounded-2xl border ${border} overflow-hidden`} style={{ transitionDelay: "200ms" }}>
              <div className={`px-6 py-4 ${isDark ? "bg-[#21262d]" : "bg-[#f6f8fa]"} border-b ${border} flex items-center gap-4`}>
                <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${isDark ? "bg-[#bc8cff]/20 text-[#bc8cff]" : "bg-[#8250df]/20 text-[#8250df]"}`}>3</span>
                <span className="font-medium">Run the application</span>
              </div>
              <div className="p-6">
                <div className={`${isDark ? "bg-[#0d1117]" : "bg-[#f6f8fa]"} rounded-xl p-4 font-mono text-sm relative group border ${border}`}>
                  <code className={isDark ? "text-[#bc8cff]" : "text-[#8250df]"}>python Hide and Seek.py</code>
                  <button
                    onClick={() => handleCopy("run", "python Hide and Seek.py")}
                    aria-label="Copy run command"
                    className={`absolute top-3 right-3 px-3 py-1.5 rounded-lg text-xs font-medium ${isDark ? "bg-[#30363d] hover:bg-[#484f58]" : "bg-[#eaeef2] hover:bg-[#d0d7de]"} opacity-0 group-hover:opacity-100 transition-all`}
                  >
                    {copiedId === "run" ? "✅" : "Copy"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── App Preview ── */}
      <section className="py-24">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-12 fade-up opacity-0 translate-y-4 transition-all duration-700">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Beautiful Interface</h2>
            <p className={`${textSec} text-lg`}>Clean, minimal design inspired by GitHub</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 fade-up opacity-0 translate-y-4 transition-all duration-700">
            {/* Encode Preview */}
            <div className={`${card} rounded-2xl border ${border} overflow-hidden shadow-2xl`}>
              <div className={`${isDark ? "bg-[#21262d]" : "bg-[#f6f8fa]"} border-b ${border} px-5 py-3 flex items-center gap-3`}>
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-[#f85149]" />
                  <div className="w-3 h-3 rounded-full bg-[#d29922]" />
                  <div className="w-3 h-3 rounded-full bg-[#3fb950]" />
                </div>
                <span className={`text-xs ${textMuted} ml-2`}>Hide and Seek — Hide</span>
              </div>
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${isDark ? "bg-[#58a6ff]/10" : "bg-[#0969da]/10"}`}>📁</div>
                  <div>
                    <div className="font-medium">Select Image</div>
                    <div className={`text-sm ${textMuted}`}>PNG, BMP, TIFF, WebP</div>
                  </div>
                </div>
                <div className={`h-28 rounded-xl border-2 border-dashed ${border} flex items-center justify-center ${textMuted}`}>
                  <span className="text-3xl mr-3">🖼</span> Drop image here
                </div>
                <div className={`h-20 rounded-xl ${isDark ? "bg-[#0d1117]" : "bg-[#f6f8fa]"} border ${border} p-4`}>
                  <div className={`text-sm ${textMuted}`}>Enter your secret message...</div>
                </div>
                <div className={`h-12 rounded-xl ${isDark ? "bg-[#238636]" : "bg-[#1a7f37]"} flex items-center justify-center text-white font-medium`}>
                  🔒  Hide
                </div>
              </div>
            </div>

            {/* Decode Preview */}
            <div className={`${card} rounded-2xl border ${border} overflow-hidden shadow-2xl`}>
              <div className={`${isDark ? "bg-[#21262d]" : "bg-[#f6f8fa]"} border-b ${border} px-5 py-3 flex items-center gap-3`}>
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-[#f85149]" />
                  <div className="w-3 h-3 rounded-full bg-[#d29922]" />
                  <div className="w-3 h-3 rounded-full bg-[#3fb950]" />
                </div>
                <span className={`text-xs ${textMuted} ml-2`}>Hide and Seek — Seek</span>
              </div>
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${isDark ? "bg-[#bc8cff]/10" : "bg-[#8250df]/10"}`}>🔍</div>
                  <div>
                    <div className="font-medium">Select Encoded Image</div>
                    <div className={`text-sm ${textMuted}`}>Image with hidden data</div>
                  </div>
                </div>
                <div className={`h-28 rounded-xl border-2 border-dashed ${border} flex items-center justify-center ${textMuted}`}>
                  <span className="text-3xl mr-3">🔍</span> Select encoded image
                </div>
                <div className={`h-12 rounded-xl ${isDark ? "bg-[#0d1117]" : "bg-[#f6f8fa]"} border ${border} flex items-center px-4`}>
                  <span className={`text-sm ${textMuted}`}>●●●●●●●● (password)</span>
                </div>
                <div className={`h-12 rounded-xl ${isDark ? "bg-[#bc8cff]" : "bg-[#8250df]"} flex items-center justify-center text-white font-medium`}>
                  🔓  Seek
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Tech Stack ── */}
      <section className={`${bgAlt} border-t ${border} py-20`}>
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-center mb-12">Built With</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: "CustomTkinter", desc: "Modern GUI", icon: "🎨" },
              { name: "Pillow", desc: "Image processing", icon: "🖼" },
              { name: "Cryptography", desc: "AES encryption", icon: "🔐" },
              { name: "NumPy", desc: "Fast arrays", icon: "🔢" },
            ].map((t, i) => (
              <div
                key={i}
                className={`fade-up opacity-0 translate-y-4 transition-all duration-500 ${card} rounded-2xl border ${border} p-5 text-center hover:shadow-lg`}
                style={{ transitionDelay: `${i * 50}ms` }}
              >
                <div className="text-3xl mb-3">{t.icon}</div>
                <div className="font-semibold">{t.name}</div>
                <div className={`text-sm ${textMuted} mt-1`}>{t.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Security ── */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-6">
          <div className={`fade-up opacity-0 translate-y-4 transition-all duration-700 ${card} rounded-2xl border ${border} p-8`}>
            <h3 className="font-bold text-xl mb-6 flex items-center gap-3">
              <span className="text-2xl">🛡️</span>
              Security Notes
            </h3>
            <ul className="space-y-4">
              {[
                "All processing is 100% local — nothing leaves your computer",
                "Encryption uses industry-standard AES-256 via Fernet",
                "PBKDF2 with 100,000 iterations for secure key derivation",
                "Output is always lossless PNG to preserve hidden data",
              ].map((item, i) => (
                <li key={i} className={`flex items-start gap-3 text-sm ${textSec}`}>
                  <span className={isDark ? "text-[#3fb950]" : "text-[#1a7f37]"}>✓</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* ── Limitations ── */}
      <section className={`${bgAlt} border-t border-b ${border} py-20`}>
        <div className="max-w-3xl mx-auto px-6">
          <div className={`fade-up opacity-0 translate-y-4 transition-all duration-700 ${card} rounded-2xl border ${isDark ? "border-[#d29922]/30" : "border-[#9a6700]/30"} p-8`}>
            <h3 className="font-bold text-xl mb-6 flex items-center gap-3">
              <span className="text-2xl">⚠️</span>
              Limitations
            </h3>
            <ul className="space-y-4">
              {[
                "JPEG images lose hidden data — lossy compression destroys LSBs. Always use lossless formats (PNG, BMP, TIFF).",
                "Image editing, resizing, or cropping destroys hidden data. Share images as-is.",
                "Without a password, anyone can decode the message. Always use encryption for sensitive data.",
                "LSB steganography can be detected by statistical analysis. Not suitable for high-security scenarios.",
              ].map((item, i) => (
                <li key={i} className={`flex items-start gap-3 text-sm ${textSec}`}>
                  <span className={isDark ? "text-[#d29922]" : "text-[#9a6700]"}>!</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className={`border-t ${border} py-10`}>
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm">
              🔐
            </div>
            <span className="font-bold">Hide and Seek</span>
            <span className={`text-xs ${textMuted}`}>v1.0</span>
          </div>
          <p className={`text-sm ${textMuted} mb-4`}>
            Open Source Image Steganography • Python + CustomTkinter
          </p>
          <a
            href="https://github.com/yourname/hide-and-seek"
            target="_blank"
            rel="noopener noreferrer"
            className={`inline-flex items-center gap-2 text-sm ${isDark ? "text-[#8b949e] hover:text-[#f0f6fc]" : "text-[#656d76] hover:text-[#1f2328]"} transition-colors`}
          >
            <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
            </svg>
            View on GitHub
          </a>
        </div>
      </footer>
    </div>
  );
}
