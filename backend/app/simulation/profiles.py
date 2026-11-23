"""
Bot Simulation Profiles — generates synthetic behavioral sessions.

Each profile produces a stream of events with specific characteristics
to test the automata-based detection engine.

Profiles:
    human_like:        Irregular timing, varied navigation, occasional idle
    scripted_bot:      Regular timing, deterministic navigation, minimal idle
    aggressive_bot:    Extremely rapid, repeated sequences, predictable
    slow_bot:          Deliberately randomized timing but deterministic behavior
    mixed:             Starts human-like, transitions to bot-like
"""

import random
import time
from typing import List, Dict, Any, Optional


PAGES = ["/", "/products", "/products/1", "/products/2", "/products/3",
         "/search", "/cart", "/login", "/checkout", "/profile"]

ELEMENTS = ["hero_banner", "nav_link", "product_card", "add_to_cart_btn",
            "search_input", "login_form", "checkout_btn", "profile_link",
            "category_filter", "sort_dropdown", "quantity_input", "remove_btn"]


def _base_event(event_type: str, timestamp: float, page: str,
                target: Optional[str] = None) -> Dict[str, Any]:
    return {
        "event_type": event_type,
        "timestamp": timestamp,
        "page": page,
        "target": target,
        "metadata": {},
    }


def generate_human_like(event_count: int = 50, pages: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Generate a human-like session.

    Characteristics:
    - Irregular timing (200ms-5s between events, with occasional long pauses)
    - Varied navigation (backtracking, search, browsing)
    - Mouse movement before clicks
    - Occasional idle periods
    - Form interaction with natural typing speed
    """
    if pages is None:
        pages = PAGES
    events = []
    ts = time.time()
    current_page = "/"

    events.append(_base_event("session_start", ts, current_page))

    for i in range(event_count - 2):
        # Irregular delay: mostly 300ms-2s, occasionally 3-8s
        if random.random() < 0.1:
            delay = random.uniform(3.0, 8.0)  # Thinking/reading pause
        elif random.random() < 0.05:
            delay = random.uniform(8.0, 15.0)  # Long idle
        else:
            delay = random.uniform(0.2, 2.5)
        ts += delay

        # Choose event type with human-like distribution
        r = random.random()
        if r < 0.15:
            # Navigate to a new page
            current_page = random.choice(pages)
            events.append(_base_event("page_view", ts, current_page))
        elif r < 0.30:
            # Mouse movement (humans move mouse a lot)
            events.append(_base_event("mouse_move", ts, current_page,
                                      random.choice(ELEMENTS)))
        elif r < 0.42:
            # Click (often preceded by move/hover)
            events.append(_base_event("mouse_click", ts, current_page,
                                      random.choice(ELEMENTS)))
        elif r < 0.52:
            # Hover
            events.append(_base_event("hover", ts, current_page,
                                      random.choice(ELEMENTS)))
        elif r < 0.62:
            # Scroll
            events.append(_base_event("scroll", ts, current_page))
        elif r < 0.70:
            # Key press (typing)
            events.append(_base_event("key_press", ts, current_page, "input_field"))
        elif r < 0.75:
            # Form focus
            events.append(_base_event("form_focus", ts, current_page, "form_field"))
        elif r < 0.78:
            # Back navigation
            events.append(_base_event("back_navigation", ts, current_page))
            current_page = random.choice(pages)
        elif r < 0.82:
            # Idle
            events.append(_base_event("idle", ts, current_page))
        elif r < 0.86:
            # Form submit
            events.append(_base_event("form_submit", ts, current_page, "form"))
        elif r < 0.90:
            # Success
            events.append(_base_event("successful_action", ts, current_page))
        elif r < 0.93:
            # Retry
            events.append(_base_event("retry", ts, current_page))
        elif r < 0.96:
            # Failed action
            events.append(_base_event("failed_action", ts, current_page))
        else:
            # Forward navigation
            events.append(_base_event("forward_navigation", ts, current_page))

    ts += random.uniform(0.5, 2.0)
    events.append(_base_event("session_end", ts, current_page))
    return events


def generate_scripted_bot(event_count: int = 50, pages: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Generate a scripted bot session.

    Characteristics:
    - Very regular timing (100-200ms between events)
    - Deterministic navigation sequence
    - Repeated action patterns
    - No idle periods
    - No mouse movement or hovering
    """
    if pages is None:
        pages = PAGES
    events = []
    ts = time.time()

    # Fixed navigation sequence repeated
    bot_sequence = ["page_view", "mouse_click", "page_view", "mouse_click",
                    "form_focus", "key_press", "key_press", "form_submit",
                    "successful_action", "page_view"]

    events.append(_base_event("session_start", ts, "/"))
    page_idx = 0

    for i in range(event_count - 2):
        # Very regular timing
        delay = random.gauss(0.15, 0.02)  # Mean 150ms, very low variance
        delay = max(0.05, delay)
        ts += delay

        event_type = bot_sequence[i % len(bot_sequence)]
        if event_type == "page_view":
            page_idx = (page_idx + 1) % len(pages)

        events.append(_base_event(event_type, ts, pages[page_idx % len(pages)],
                                  ELEMENTS[i % len(ELEMENTS)]))

    ts += 0.15
    events.append(_base_event("session_end", ts, pages[page_idx % len(pages)]))
    return events


def generate_aggressive_bot(event_count: int = 50, pages: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Generate an aggressive automation session.

    Characteristics:
    - Extremely rapid events (10-50ms)
    - Repeated identical actions
    - Predictable linear navigation
    - No variation
    """
    if pages is None:
        pages = PAGES
    events = []
    ts = time.time()

    events.append(_base_event("session_start", ts, "/"))

    # Aggressive pattern: rapid clicks through every page
    for i in range(event_count - 2):
        delay = random.uniform(0.01, 0.05)  # 10-50ms
        ts += delay

        page = pages[i % len(pages)]
        # Almost all clicks, very few other events
        if i % 5 == 0:
            events.append(_base_event("page_view", ts, page))
        else:
            events.append(_base_event("mouse_click", ts, page, "add_to_cart_btn"))

    ts += 0.02
    events.append(_base_event("session_end", ts, "/"))
    return events


def generate_slow_bot(event_count: int = 50, pages: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Generate a slow bot session.

    Characteristics:
    - Deliberately randomized timing (mimics human delays)
    - Still follows deterministic navigation patterns
    - Low interaction diversity
    - Suspiciously consistent behavior despite timing variation
    """
    if pages is None:
        pages = PAGES
    events = []
    ts = time.time()

    # Same deterministic sequence but with human-like delays
    bot_sequence = ["page_view", "mouse_click", "page_view", "mouse_click",
                    "form_focus", "key_press", "form_submit", "page_view",
                    "mouse_click", "page_view"]

    events.append(_base_event("session_start", ts, "/"))
    page_idx = 0

    for i in range(event_count - 2):
        # Deliberately randomized but the pattern is still deterministic
        delay = random.uniform(0.3, 3.0)
        ts += delay

        event_type = bot_sequence[i % len(bot_sequence)]
        if event_type == "page_view":
            page_idx = (page_idx + 1) % len(pages)

        events.append(_base_event(event_type, ts, pages[page_idx % len(pages)],
                                  ELEMENTS[0]))  # Always same element

    ts += random.uniform(0.5, 1.5)
    events.append(_base_event("session_end", ts, pages[0]))
    return events


def generate_mixed(event_count: int = 50, pages: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Generate a mixed behavior session.

    Starts human-like, transitions to bot-like behavior midway.
    Tests whether the automata can detect the behavioral shift.
    """
    half = event_count // 2
    human_events = generate_human_like(half + 1, pages)
    # Remove session_end from human part
    human_events = [e for e in human_events if e["event_type"] != "session_end"]

    bot_events = generate_aggressive_bot(half + 1, pages)
    # Remove session_start from bot part, adjust timestamps
    bot_events = [e for e in bot_events if e["event_type"] not in ("session_start", "session_end")]

    if human_events:
        last_ts = human_events[-1]["timestamp"]
        for e in bot_events:
            e["timestamp"] = last_ts + (e["timestamp"] - bot_events[0]["timestamp"]) + 0.5

    combined = human_events + bot_events
    # Add session_end
    if combined:
        combined.append(_base_event("session_end", combined[-1]["timestamp"] + 0.5,
                                    combined[-1]["page"]))

    return combined[:event_count]


PROFILES = {
    "human_like": generate_human_like,
    "scripted_bot": generate_scripted_bot,
    "aggressive_bot": generate_aggressive_bot,
    "slow_bot": generate_slow_bot,
    "mixed": generate_mixed,
}
