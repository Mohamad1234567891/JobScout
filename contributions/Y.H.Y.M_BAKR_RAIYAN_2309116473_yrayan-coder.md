# Contribution Report — Y.H.Y.M Bakr Raiyan

**Student Name:** Y.H.Y.M Bakr Raiyan  
**Student ID:** 2309116473  
**GitHub Username:** [yrayan-coder](https://github.com/yrayan-coder)  
**Project:** JobScout  
**Role:** GUI Development — Sidebar Components

---

## Overview

As a member of the JobScout team, I was responsible for developing and integrating the sidebar interface. My work focused on creating reusable GUI components, implementing a scrollable sidebar container, and organizing the sidebar action items.

I created the action item component with a title and three-dot button, added a dedicated scrolling container to arrange items vertically, and integrated the components into the sidebar. This provides a flexible foundation for future sidebar features and navigation functionality.

---

## Detailed Contributions

### 1. Sidebar Action Item Component

**File:** `src/GUI/Components/Action_item.py`

I created a reusable `ActionItem` component for the JobScout GUI
sidebar.

-   Added an action item that displays a title.
-   Added a three-dot button on the right side of each item.
-   Kept the three-dot button visual only; it currently has no
    functionality.
-   Connected clicking the action title to a placeholder callback, ready
    for future implementation.
-   Styled the component to fit the application's dark sidebar
    appearance.

### 2. Scrollable Sidebar Container

**File:** `src/GUI/Components/Scroll.py`

I added a separate `SidebarScrollContainer` class while preserving the
existing `ScrollContainer` used elsewhere in the application.

-   Used `QScrollArea` to support scrolling when the sidebar contains
    more items than fit vertically.
-   Used `QVBoxLayout` to arrange action items vertically.
-   Added an `add_item()` method so sidebar items can be inserted into
    the layout and automatically placed one below another.
-   Preserved the existing product-card scroll container to avoid
    disrupting its functionality.

### 3. Sidebar Integration

**File:** `src/GUI/Components/Sidebar.py`

I integrated the action item component and the new scroll container into
the JobScout sidebar.

The sidebar currently contains these four placeholder entries:

1.  Dashboard
2.  Job Search
3.  Saved Jobs
4.  Application Tracker

These entries are currently UI placeholders. Their actual
page/navigation functionality is intended for future development.

## Contribution Summary

My contribution to JobScout focused on building and integrating the sidebar UI:

- Created a reusable sidebar action item.
- Added a three-dot visual control and placeholder click behavior.
- Implemented a vertical, scrollable container for sidebar items.
- Integrated Dashboard, Job Search, Saved Jobs, and Application Tracker into the sidebar.

These contributions provide a reusable and expandable sidebar structure for future JobScout functionality.

