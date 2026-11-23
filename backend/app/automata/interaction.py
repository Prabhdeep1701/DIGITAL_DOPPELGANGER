"""
Interaction Automaton — tracks user interaction patterns.

Monitors:
- Click, hover, keyboard, scroll, form interactions
- Natural interaction flow vs mechanical patterns
- Form completion behavior
- Interaction diversity
"""

from app.automata.base import DFA

STATES = {
    "START",
    "IDLE_STATE",
    "MOVING",
    "HOVERING",
    "CLICKING",
    "SCROLLING",
    "FORM_INPUT",
    "FORM_COMPLETING",
    "RAPID_CLICKING",
    "MECHANICAL_INTERACTION",
    "DIVERSE_INTERACTION",
    "SUSPICIOUS_INTERACTION",
    "END",
}

ACCEPTING = {"END", "DIVERSE_INTERACTION", "IDLE_STATE", "FORM_COMPLETING", "MOVING", "HOVERING", "SCROLLING"}
SUSPICIOUS = {"RAPID_CLICKING", "MECHANICAL_INTERACTION", "SUSPICIOUS_INTERACTION"}


def create_interaction_automaton() -> DFA:
    """
    Build the interaction DFA.

    Humans exhibit diverse, varied interactions with natural pauses.
    Bots tend to use minimal interaction types in mechanical patterns.
    """
    transitions = {
        "START": {
            "MOVE": "MOVING",
            "CLICK": "CLICKING",
            "PAGE_VIEW": "IDLE_STATE",
            "START": "IDLE_STATE",
            "*": "IDLE_STATE",
        },
        "IDLE_STATE": {
            "MOVE": "MOVING",
            "CLICK": "CLICKING",
            "HOVER": "HOVERING",
            "SCROLL": "SCROLLING",
            "KEY": "FORM_INPUT",
            "FOCUS": "FORM_INPUT",
            "PAGE_VIEW": "IDLE_STATE",
            "IDLE": "IDLE_STATE",
            "RAPID_ACTION": "SUSPICIOUS_INTERACTION",
            "REPEATED_ACTION": "MECHANICAL_INTERACTION",
            "END": "END",
            "*": "IDLE_STATE",
        },
        "MOVING": {
            "CLICK": "CLICKING",
            "HOVER": "HOVERING",
            "MOVE": "MOVING",
            "SCROLL": "DIVERSE_INTERACTION",
            "IDLE": "IDLE_STATE",
            "KEY": "FORM_INPUT",
            "FOCUS": "FORM_INPUT",
            "PAGE_VIEW": "IDLE_STATE",
            "RAPID_ACTION": "SUSPICIOUS_INTERACTION",
            "END": "END",
            "*": "MOVING",
        },
        "HOVERING": {
            "CLICK": "DIVERSE_INTERACTION",  # Hover then click is human-like
            "MOVE": "MOVING",
            "HOVER": "HOVERING",
            "SCROLL": "SCROLLING",
            "IDLE": "IDLE_STATE",
            "PAGE_VIEW": "IDLE_STATE",
            "KEY": "FORM_INPUT",
            "RAPID_ACTION": "SUSPICIOUS_INTERACTION",
            "END": "END",
            "*": "HOVERING",
        },
        "CLICKING": {
            "CLICK": "RAPID_CLICKING",  # Immediate double-click
            "MOVE": "DIVERSE_INTERACTION",
            "HOVER": "DIVERSE_INTERACTION",
            "SCROLL": "DIVERSE_INTERACTION",
            "KEY": "FORM_INPUT",
            "FOCUS": "FORM_INPUT",
            "PAGE_VIEW": "IDLE_STATE",
            "IDLE": "IDLE_STATE",
            "SUBMIT": "FORM_COMPLETING",
            "SUCCESS": "IDLE_STATE",
            "FAILURE": "IDLE_STATE",
            "RAPID_ACTION": "SUSPICIOUS_INTERACTION",
            "REPEATED_ACTION": "MECHANICAL_INTERACTION",
            "END": "END",
            "*": "CLICKING",
        },
        "SCROLLING": {
            "SCROLL": "SCROLLING",
            "CLICK": "DIVERSE_INTERACTION",
            "MOVE": "MOVING",
            "HOVER": "HOVERING",
            "IDLE": "IDLE_STATE",
            "PAGE_VIEW": "IDLE_STATE",
            "RAPID_ACTION": "SUSPICIOUS_INTERACTION",
            "END": "END",
            "*": "SCROLLING",
        },
        "FORM_INPUT": {
            "KEY": "FORM_INPUT",
            "FOCUS": "FORM_INPUT",
            "CLICK": "FORM_INPUT",
            "SUBMIT": "FORM_COMPLETING",
            "MOVE": "FORM_INPUT",
            "IDLE": "IDLE_STATE",
            "PAGE_VIEW": "IDLE_STATE",
            "RAPID_ACTION": "SUSPICIOUS_INTERACTION",
            "REPEATED_ACTION": "MECHANICAL_INTERACTION",
            "END": "END",
            "*": "FORM_INPUT",
        },
        "FORM_COMPLETING": {
            "SUCCESS": "DIVERSE_INTERACTION",
            "FAILURE": "IDLE_STATE",
            "PAGE_VIEW": "IDLE_STATE",
            "CLICK": "CLICKING",
            "RETRY": "FORM_INPUT",
            "IDLE": "IDLE_STATE",
            "END": "END",
            "*": "IDLE_STATE",
        },
        "RAPID_CLICKING": {
            "CLICK": "SUSPICIOUS_INTERACTION",  # 3+ rapid clicks
            "MOVE": "CLICKING",  # Movement breaks the pattern
            "HOVER": "CLICKING",
            "IDLE": "IDLE_STATE",
            "SCROLL": "SCROLLING",
            "PAGE_VIEW": "IDLE_STATE",
            "RAPID_ACTION": "SUSPICIOUS_INTERACTION",
            "END": "END",
            "*": "RAPID_CLICKING",
        },
        "DIVERSE_INTERACTION": {
            "CLICK": "CLICKING",
            "MOVE": "MOVING",
            "HOVER": "HOVERING",
            "SCROLL": "SCROLLING",
            "KEY": "FORM_INPUT",
            "FOCUS": "FORM_INPUT",
            "IDLE": "IDLE_STATE",
            "PAGE_VIEW": "IDLE_STATE",
            "SUBMIT": "FORM_COMPLETING",
            "REPEATED_ACTION": "MECHANICAL_INTERACTION",
            "END": "END",
            "*": "DIVERSE_INTERACTION",
        },
        "MECHANICAL_INTERACTION": {
            "REPEATED_ACTION": "SUSPICIOUS_INTERACTION",
            "IDLE": "IDLE_STATE",
            "MOVE": "MOVING",
            "HOVER": "HOVERING",
            "CLICK": "CLICKING",
            "KEY": "FORM_INPUT",
            "END": "END",
            "*": "MECHANICAL_INTERACTION",
        },
        "SUSPICIOUS_INTERACTION": {
            "IDLE": "IDLE_STATE",  # Idle de-escalates
            "MOVE": "MOVING",
            "HOVER": "HOVERING",
            "END": "END",
            "*": "SUSPICIOUS_INTERACTION",
        },
        "END": {
            "*": "END",
        },
    }

    return DFA(
        name="interaction",
        states=STATES,
        alphabet=set(transitions.get("IDLE_STATE", {}).keys()) | {"START", "END"},
        transitions=transitions,
        start_state="START",
        accepting_states=ACCEPTING,
        suspicious_states=SUSPICIOUS,
    )
