import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

function AnimatedSection({
  children,
  className = "",
  delay = 0,
  threshold = 0.2,
}) {
  const ref = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(node);
        }
      },
      { threshold }
    );

    observer.observe(node);

    return () => observer.disconnect();
  }, [threshold]);

  return (
    <div
      ref={ref}
      className={`transform transition-all duration-1000 ease-out ${
        isVisible ? "translate-y-0 opacity-100" : "translate-y-12 opacity-0"
      } ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

function PixelStar({ className = "", delay = 0, size = 10 }) {
  return (
    <div
      className={`pixel-star ${className}`}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        animationDelay: `${delay}ms`,
      }}
    />
  );
}

function StarTextBlock({
  children,
  starsDelay = 700,
  align = "center",
  className = "",
}) {
  const alignmentClass =
    align === "left"
      ? "stars-left"
      : align === "right"
      ? "stars-right"
      : "stars-center";

  return (
    <div className={`relative inline-block max-w-full ${className}`}>
      <div>{children}</div>

      <div
        className={`text-stars pointer-events-none absolute inset-0 ${alignmentClass}`}
        style={{ animationDelay: `${starsDelay}ms` }}
      >
        <PixelStar className="-left-6 top-2" delay={0} size={7} />
        <PixelStar className="left-[8%] -top-5" delay={180} size={8} />
        <PixelStar className="left-[20%] top-full mt-2" delay={340} size={7} />
        <PixelStar className="left-[38%] -top-7" delay={500} size={8} />
        <PixelStar className="right-[36%] top-full mt-1" delay={130} size={7} />
        <PixelStar className="right-[18%] -top-5" delay={390} size={8} />
        <PixelStar className="-right-5 top-3" delay={250} size={7} />
        <PixelStar className="right-[7%] top-[78%]" delay={560} size={6} />
      </div>
    </div>
  );
}

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <>
      <style>
        {`
          .hide-scrollbar {
            -ms-overflow-style: none;
            scrollbar-width: none;
          }

          .hide-scrollbar::-webkit-scrollbar {
            display: none;
          }

          @keyframes text-fade-up {
            0% {
              opacity: 0;
              transform: translateY(24px);
            }
            100% {
              opacity: 1;
              transform: translateY(0);
            }
          }

          @keyframes stars-appear {
            0% {
              opacity: 0;
            }
            100% {
              opacity: 1;
            }
          }

          @keyframes star-twinkle {
            0%, 100% {
              opacity: 0.55;
            }
            50% {
              opacity: 1;
            }
          }

          .hero-text {
            animation: text-fade-up 900ms ease-out forwards;
            will-change: transform, opacity;
          }

          .text-stars {
            opacity: 0;
            animation: stars-appear 180ms linear forwards;
          }

          .stars-center {
            transform: none;
          }

          .stars-left {
            transform: translateX(-10px);
          }

          .stars-right {
            transform: translateX(10px);
          }

          .pixel-star {
            position: absolute;
            background: white;
            box-shadow:
              0 0 0 1px rgba(255, 255, 255, 0.95),
              0 0 8px rgba(255, 255, 255, 0.45);
            animation: star-twinkle 1200ms steps(2, end) infinite;
          }

          .pixel-star::before,
          .pixel-star::after {
            content: "";
            position: absolute;
            background: white;
          }

          .pixel-star::before {
            left: 50%;
            top: -45%;
            width: 2px;
            height: 190%;
            transform: translateX(-50%);
          }

          .pixel-star::after {
            top: 50%;
            left: -45%;
            width: 190%;
            height: 2px;
            transform: translateY(-50%);
          }
        `}
      </style>

      <div className="hide-scrollbar h-screen overflow-y-auto bg-[#0f172a]">
        <main className="mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-12 sm:px-10 md:px-16">
          <section className="flex min-h-screen items-center justify-center">
            <div className="relative w-full text-center">
              <div className="hero-text">
                <StarTextBlock starsDelay={1000} align="center">
                  <h1 className="font-madimi text-5xl text-white sm:text-6xl md:text-7xl">
                    Welcome to <span className="text-blue-pastel">moodscape</span>!
                  </h1>
                </StarTextBlock>
              </div>
            </div>
          </section>

          <section className="flex min-h-[85vh] items-center">
            <AnimatedSection delay={100} className="w-full" threshold={0.25}>
              <StarTextBlock starsDelay={950} align="left">
                <>
                  <h2 className="mb-6 font-madimi text-3xl text-red-pastel sm:text-4xl">
                    A place where music becomes visible
                  </h2>
                  <p className="max-w-3xl font-afacad text-2xl leading-relaxed text-white sm:text-3xl">
                    Moodscape transforms musical emotion into an interactive visual
                    experience. Explore how songs carry shades of anger,
                    anticipation, happiness, disgust, sadness, and fear across time
                    and discover patterns that are hard to notice through sound
                    alone.
                  </p>
                </>
              </StarTextBlock>
            </AnimatedSection>
          </section>

          <section className="flex min-h-[85vh] items-center justify-end">
            <AnimatedSection
              delay={100}
              className="w-full max-w-3xl text-right"
              threshold={0.25}
            >
              <StarTextBlock starsDelay={950} align="right">
                <>
                  <h2 className="mb-6 font-madimi text-3xl text-orange-pastel sm:text-4xl">
                    Scroll through emotion
                  </h2>
                  <p className="font-afacad text-2xl leading-relaxed text-white sm:text-3xl">
                    Each visualization is designed to help you move through large
                    collections of songs in an intuitive way. Instead of reading raw
                    numbers, you can follow shapes, colors, and motion to understand
                    how emotional components shift between years, tracks, and moods.
                  </p>
                </>
              </StarTextBlock>
            </AnimatedSection>
          </section>

          <section className="flex min-h-[85vh] items-center">
            <AnimatedSection delay={100} className="w-full" threshold={0.25}>
              <StarTextBlock starsDelay={950} align="left">
                <>
                  <h2 className="mb-6 font-madimi text-3xl text-yellow-pastel sm:text-4xl">
                    Built for exploration
                  </h2>
                  <p className="max-w-3xl font-afacad text-2xl leading-relaxed text-white sm:text-3xl">
                    Filter, compare, and navigate through the data in a way that
                    feels playful but still informative. The goal is not only to see
                    which moods appear in songs, but also to experience how they
                    relate to one another in a living visual landscape.
                  </p>
                </>
              </StarTextBlock>
            </AnimatedSection>
          </section>

          <section className="flex min-h-screen items-center justify-center">
            <AnimatedSection
              delay={100}
              className="w-full text-center"
              threshold={0.2}
            >
                <p className="mb-10 font-madimi text-3xl leading-relaxed text-white sm:text-4xl">
                  Ready to enter the visualization?
                </p>

              <div className="flex items-center justify-center gap-4 sm:gap-8">
                <img
                  src="/meymuni.gif"
                  alt="Left gif"
                  className="h-20 w-20 object-contain sm:h-28 sm:w-28"
                />

                <button
                  type="button"
                  onClick={() => navigate("/visualization")}
                  className="rounded-lg bg-blue-pastel px-8 py-4 font-madimi text-xl text-white shadow-lg transition-transform duration-300 hover:scale-105"
                >
                  Go to vizualization
                </button>

                <img
                  src="/meymuni.gif"
                  alt="Right gif"
                  className="h-20 w-20 object-contain sm:h-28 sm:w-28"
                />
              </div>
            </AnimatedSection>
          </section>
        </main>
      </div>
    </>
  );
}