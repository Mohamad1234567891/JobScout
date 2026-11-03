# contribution Report — Abdulmalik Mahmoud

**Student Name:** Abdulmalik Mahmoud
**Student ID:** 2609115237
**GitHub Username:** abdulmalik108

**Project: JobScout**
**Role: Team Member** — Desktop Notifications

## Overview
I was responsible for JobScout's desktop notification system: the part that alerts the user when the background search finds a job that matches them. My task was to find a single notification API that works on Windows, macOS and Linux, and to wrap it in one simple function the rest of the application can call without caring which operating system it runs on.

## 1. Research — Choosing a Cross-Platform Notification API
Researched how desktop notifications work on each operating system (Windows toast notifications, the macOS Notification Center, and the Linux freedesktop D-Bus notification service).
Compared Python libraries that wrap all three, and chose desktop-notifier, because it uses each platform's native notification system through one shared API and is actively maintained.
Identified platform caveats for the team: on macOS, notifications only work from a signed Python executable (the python.org installer works, Homebrew's does not); on Linux, extra features such as buttons depend on the desktop environment; and on Windows, the sender currently appears as "Python" until the app is packaged.
## 2. Notification Module — src/Core/Notifications/
Created the Notifications package inside src/Core/, following the project's existing folder and naming conventions (Notifications/__init__.py and Notifications/notifier.py).
notifier.py — implemented send_notification(title, message), a single OS-independent function that shows a native desktop notification. It uses the synchronous DesktopNotifierSync class with a single shared notifier instance named "JobScout", so no async setup is needed by the caller.
Documented the function with type hints and a docstring so teammates can see how to use it directly from their editor.
Added a self-test block (if __name__ == "__main__") so the module can be run on its own to confirm notifications work on a machine, without triggering popups when it is imported by the rest of the app.
## 3. Dependencies & Version Control
Added desktop-notifier to requirements.txt so the dependency is installed automatically with the rest of the project.
Developed the feature on a separate notifications branch, pushed it to GitHub and opened a pull request for the team leader to review and merge into main.
## 4. Testing
Tested the notification module on Windows and confirmed that native notifications appear correctly.
After the merge, set up the full project with Setup.py and tested JobScout end-to-end through the graphical interface.