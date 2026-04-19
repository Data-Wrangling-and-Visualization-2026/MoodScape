import { useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import SongPointPopup from "../ui/SongPointPopup";

const VIEWPORT_PADDING = 12;
const POPUP_GAP = 12;

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

export default function SongDataPoint({
  song,
  size = 16,
  isActive = false,
  activeColor = "white",
  onMouseEnter,
  onMouseLeave,
  onClick,
  pointX = 0,
  pointY = 0,
  boxWidth = 0,
  boxHeight = 0,
}) {
  const buttonRef = useRef(null);
  const popupRef = useRef(null);

  const [isHovered, setIsHovered] = useState(false);

  const [popupStyle, setPopupStyle] = useState({
    top: 0,
    left: 0,
  });

  const isShown = isActive || isHovered;
  const currentSize = isShown ? size * 1.25 : size;

  useLayoutEffect(() => {
    if (!isShown) return;

    const updatePopupPosition = () => {
      const buttonEl = buttonRef.current;
      const popupEl = popupRef.current;

      if (!buttonEl || !popupEl) return;

      const buttonRect = buttonEl.getBoundingClientRect();
      const popupRect = popupEl.getBoundingClientRect();

      const scrollContainer = buttonEl.closest(
        "[data-graph-scroll-container='true']",
      );

      const containerRect = scrollContainer
        ? scrollContainer.getBoundingClientRect()
        : {
            left: 0,
            top: 0,
            right: window.innerWidth,
            bottom: window.innerHeight,
            width: window.innerWidth,
            height: window.innerHeight,
          };

      const visibleLeft = Math.max(containerRect.left, VIEWPORT_PADDING);
      const visibleTop = Math.max(containerRect.top, VIEWPORT_PADDING);
      const visibleRight = Math.min(
        containerRect.left + (boxWidth || containerRect.width),
        window.innerWidth - VIEWPORT_PADDING,
      );
      const visibleBottom = Math.min(
        containerRect.top + (boxHeight || containerRect.height),
        window.innerHeight - VIEWPORT_PADDING,
      );

      const spaceOnRight = visibleRight - buttonRect.right;
      const spaceOnLeft = buttonRect.left - visibleLeft;

      let left;

      const fitsRight = spaceOnRight >= popupRect.width + POPUP_GAP;
      const fitsLeft = spaceOnLeft >= popupRect.width + POPUP_GAP;

      if (fitsRight) {
        left = buttonRect.right + POPUP_GAP;
      } else if (fitsLeft) {
        left = buttonRect.left - popupRect.width - POPUP_GAP;
      } else {
        const preferredLeft = buttonRect.right + POPUP_GAP;
        left = clamp(
          preferredLeft,
          visibleLeft,
          Math.max(visibleLeft, visibleRight - popupRect.width),
        );
      }

      let top = buttonRect.top + buttonRect.height / 2 - popupRect.height / 2;

      if (top + popupRect.height > visibleBottom) {
        top = visibleBottom - popupRect.height - VIEWPORT_PADDING;
      }

      if (top < visibleTop) {
        top = visibleTop;
      }

      setPopupStyle({
        top,
        left,
      });
    };

    updatePopupPosition();

    window.addEventListener("resize", updatePopupPosition);
    window.addEventListener("scroll", updatePopupPosition, true);

    return () => {
      window.removeEventListener("resize", updatePopupPosition);
      window.removeEventListener("scroll", updatePopupPosition, true);
    };
  }, [isShown, song, pointX, pointY, boxWidth, boxHeight]);

  const handleMouseEnter = (event) => {
    setIsHovered(true);
    onMouseEnter?.(event);
  };

  const handleMouseLeave = (event) => {
    setIsHovered(false);
    onMouseLeave?.(event);
  };

  const handleClick = (event) => {
    event.stopPropagation();
    onClick?.(event);
  };

  return (
    <div
      className="relative inline-flex items-center justify-center"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <button
        ref={buttonRef}
        type="button"
        aria-label={`Open info for ${song.title}`}
        onClick={handleClick}
        className="cursor-pointer rounded-full transition-all duration-200 ease-out"
        style={{
          width: `${currentSize}px`,
          height: `${currentSize}px`,
          backgroundColor: isShown ? activeColor : "white",
          boxShadow: isShown
            ? `0 0 10px ${activeColor}`
            : "0 0 4px rgba(0,0,0,0.4)",
        }}
      />

      {isShown &&
        typeof document !== "undefined" &&
        createPortal(
          <div
            ref={popupRef}
            className="fixed z-[1000000]"
            style={{
              top: `${popupStyle.top}px`,
              left: `${popupStyle.left}px`,
            }}
          >
            <SongPointPopup song={song} />
          </div>,
          document.body,
        )}
    </div>
  );
}
