#!/usr/bin/env python3
"""
Pomodoro Timer with Enhanced Visual Feedback (Pattern A)

Features:
- Circular progress bar with smooth animation
- Color transitions (blue → yellow → red) based on remaining time
- Background effects (particles and ripples) during focus sessions
- Customizable timer settings
- Session tracking and statistics
"""

from pomodoro_gui import PomodoroGUI

if __name__ == "__main__":
    # Create and run the Pomodoro Timer application
    app = PomodoroGUI()
    app.run()
