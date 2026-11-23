"""
Navigation Automaton — tracks page transition patterns.

Monitors:
- Page transitions and navigation flow
- Back/forward navigation
- Repeated page visits
- Impossible navigation sequences
"""

from app.automata.base import DFA

STATES = {
    "START",
    "LANDING",
    "BROWSING",
    "DEEP_BROWSING",
    "NAVIGATING_BACK",
    "NAVIGATING_FORWARD",
    "SEARCHING",
    "REPEATED_NAVIGATION",
    "LINEAR_NAVIGATION",
    "ERRATIC_NAVIGATION",
    "SUSPICIOUS_NAVIGATION",
    "END",
}

ACCEPTING = {"END", "LANDING", "BROWSING", "DEEP_BROWSING", "NAVIGATING_BACK", "SEARCHING"}
SUSPICIOUS = {"REPEATED_NAVIGATION", "LINEAR_NAVIGATION", "ERRATIC_NAVIGATION", "SUSPICIOUS_NAVIGATION"}


def create_navigation_automaton() -> DFA:
    """
    Build the navigation DFA.

    Tracks how a user navigates between pages. Human users tend to browse
    non-linearly with backtracking, while bots follow predictable paths.
    """
    transitions = {
        "START": {
            "PAGE_VIEW": "LANDING",
            "START": "START",
            "*": "START",
        },
        "LANDING": {
            "PAGE_VIEW": "BROWSING",
            "CLICK": "BROWSING",
            "MOVE": "LANDING",
            "HOVER": "LANDING",
            "SCROLL": "LANDING",
            "KEY": "SEARCHING",
            "IDLE": "LANDING",
            "END": "END",
            "*": "LANDING",
        },
        "BROWSING": {
            "PAGE_VIEW": "DEEP_BROWSING",
            "CLICK": "BROWSING",
            "BACK": "NAVIGATING_BACK",
            "FORWARD": "NAVIGATING_FORWARD",
            "MOVE": "BROWSING",
            "HOVER": "BROWSING",
            "SCROLL": "BROWSING",
            "KEY": "SEARCHING",
            "FOCUS": "BROWSING",
            "SUBMIT": "BROWSING",
            "IDLE": "BROWSING",
            "REPEATED_ACTION": "REPEATED_NAVIGATION",
            "END": "END",
            "*": "BROWSING",
        },
        "DEEP_BROWSING": {
            "PAGE_VIEW": "LINEAR_NAVIGATION",  # 3+ page views without other actions
            "CLICK": "BROWSING",
            "BACK": "NAVIGATING_BACK",
            "FORWARD": "NAVIGATING_FORWARD",
            "MOVE": "DEEP_BROWSING",
            "HOVER": "DEEP_BROWSING",
            "SCROLL": "DEEP_BROWSING",
            "KEY": "SEARCHING",
            "IDLE": "DEEP_BROWSING",
            "REPEATED_ACTION": "REPEATED_NAVIGATION",
            "RAPID_ACTION": "SUSPICIOUS_NAVIGATION",
            "END": "END",
            "*": "DEEP_BROWSING",
        },
        "NAVIGATING_BACK": {
            "PAGE_VIEW": "BROWSING",
            "BACK": "ERRATIC_NAVIGATION",  # Double-back is unusual
            "CLICK": "BROWSING",
            "MOVE": "BROWSING",
            "IDLE": "BROWSING",
            "END": "END",
            "*": "BROWSING",
        },
        "NAVIGATING_FORWARD": {
            "PAGE_VIEW": "BROWSING",
            "FORWARD": "ERRATIC_NAVIGATION",
            "CLICK": "BROWSING",
            "MOVE": "BROWSING",
            "END": "END",
            "*": "BROWSING",
        },
        "SEARCHING": {
            "KEY": "SEARCHING",
            "CLICK": "BROWSING",
            "PAGE_VIEW": "BROWSING",
            "SUBMIT": "BROWSING",
            "IDLE": "BROWSING",
            "REPEATED_ACTION": "REPEATED_NAVIGATION",
            "END": "END",
            "*": "BROWSING",
        },
        "REPEATED_NAVIGATION": {
            "PAGE_VIEW": "SUSPICIOUS_NAVIGATION",
            "CLICK": "SUSPICIOUS_NAVIGATION",
            "REPEATED_ACTION": "SUSPICIOUS_NAVIGATION",
            "IDLE": "BROWSING",  # Idle can reset suspicion
            "END": "END",
            "*": "REPEATED_NAVIGATION",
        },
        "LINEAR_NAVIGATION": {
            "PAGE_VIEW": "SUSPICIOUS_NAVIGATION",  # 4+ linear pages = very suspicious
            "BACK": "BROWSING",  # Backtracking reduces suspicion
            "CLICK": "BROWSING",
            "MOVE": "BROWSING",
            "HOVER": "BROWSING",
            "IDLE": "BROWSING",
            "END": "END",
            "*": "LINEAR_NAVIGATION",
        },
        "ERRATIC_NAVIGATION": {
            "PAGE_VIEW": "BROWSING",
            "CLICK": "BROWSING",
            "IDLE": "BROWSING",
            "BACK": "SUSPICIOUS_NAVIGATION",
            "FORWARD": "SUSPICIOUS_NAVIGATION",
            "END": "END",
            "*": "BROWSING",
        },
        "SUSPICIOUS_NAVIGATION": {
            "IDLE": "BROWSING",  # Idle can de-escalate
            "BACK": "BROWSING",
            "MOVE": "BROWSING",
            "HOVER": "BROWSING",
            "END": "END",
            "*": "SUSPICIOUS_NAVIGATION",
        },
        "END": {
            "*": "END",
        },
    }

    return DFA(
        name="navigation",
        states=STATES,
        alphabet=set(transitions.get("BROWSING", {}).keys()) | {"START", "END"},
        transitions=transitions,
        start_state="START",
        accepting_states=ACCEPTING,
        suspicious_states=SUSPICIOUS,
    )
