---
name: Complaint Review
description: A simple native Streamlit dashboard for a classroom complaint-triage experiment.
colors:
  primary: "#12616C"
  background: "#FFFFFF"
  light-neutral: "#F3F6F6"
  ink: "#001318"
typography:
  body:
    fontFamily: "sans-serif"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.background}"
  input:
    backgroundColor: "{colors.light-neutral}"
    textColor: "{colors.ink}"
  sidebar:
    backgroundColor: "{colors.light-neutral}"
    textColor: "{colors.ink}"
---

# Design System: Complaint Review

## Overview

The current interface expresses the user's simple, clean direction through native Streamlit forms, clear headings, short explanatory copy, and tabular evidence. A white main surface and light neutral controls support a single teal accent.

This document records the implemented dashboard. Streamlit owns its control geometry, interactive states, and responsive behavior. The theme values in `.streamlit/config.toml` are the source of the tokens above.

**Key Characteristics:**

- One sidebar for navigation and the shared cutoff.
- Four workspaces: Ticket assessment, Batch processing, Analytics and Dataset. Presentation guidance stays in a separate PDF.
- Native tables, charts, expanders, and status messages.
- Visible captions for provenance and model limitations.

## Colors

The palette combines a restrained teal accent with white, pale neutral surfaces, and dark text.

### Primary

- **Teal** (`primary`): primary submit/download actions, selected radio markers, the cutoff slider, and native sample-data bar charts.

### Neutral

- **White** (`background`): the main page and primary-button text.
- **Light Neutral** (`light-neutral`): the sidebar and filled input surfaces.
- **Dark Ink** (`ink`): the configured text color.

**The Native Status Rule.** Use Streamlit's semantic information, warning, and error components for feedback. Their framework-provided colors are not additional project palette tokens.

## Typography

The theme selects Streamlit's native sans serif option. No custom font, numeric type scale, or letter-spacing tokens are authored in this project.

Use `st.title` for the page task, `st.subheader` for result and evidence sections, ordinary text for explanations, and `st.caption` for supporting context. Labels remain in sentence case. Preserve the framework's heading and body hierarchy.

## Layout

The app uses Streamlit's wide layout. Desktop shows a left sidebar and a main content column. Four navigation choices open ticket assessment, batch processing, analytics and the dataset. Saved-model context and provenance remain visible; the threshold control is inside Routing settings. Reset workspace returns to a blank assessment and the saved threshold.

Ticket context fields use two columns on desktop. The observed mobile layout collapses the sidebar and stacks these columns into a single vertical form; the heading wraps naturally. Tables and figures stretch to the available main-column width. No custom breakpoint or spacing scale is authored.

## Elevation & Depth

The resting interface is flat. Pale input/sidebar surfaces, thin native borders, and dividers separate regions. The project authors no shadow or motion tokens; keep Streamlit's own interaction behavior.

## Shapes

Native controls and the form use gently rounded corners. Inputs are filled pale rectangles; the form and collapsed expanders have thin borders. Radius and border measurements are framework-owned and are intentionally absent from the token frontmatter.

## Components

### Buttons

Primary actions use `type="primary"`, giving them the teal treatment. Ticket assessment is the form's submit action; batch CSV download is also primary. Other downloads use the native secondary treatment. Preserve native hover, focus, disabled, and pressed states.

### Inputs / Fields

Use labeled native text areas, selectboxes, number inputs, sliders, checkboxes, and file uploaders. Complaint text spans the form width, with contextual fields below. Numeric help text explains elapsed response time. Empty complaint text produces a native error; invalid CSV feedback appears beside the upload workflow.

### Navigation

A single sidebar radio group contains the four workspace destinations. Its selected marker uses the primary accent. The native sidebar can collapse on mobile. Keep navigation separate from the page-specific sample-data tabs.

### Forms / Containers

The ticket form groups editable inputs and an explicit assessment action. Results appear below a divider, with a recommendation heading, score/cutoff text, supporting caption, native information message, input-details expander, and download.

### Evidence and Progressive Disclosure

Use native tables for confusion counts, dataframes for metrics, predictions and previews, and captioned report figures. Results lead with error counts and four summary metrics. Model comparison, importance, cutoff analysis and technical charts live in optional expanders. Sample-data exploration starts with one inspectable row and offers a 12-row record preview and uses three native tabs.

## Do's and Don'ts

### Do:

- **Do** preserve the single sidebar and labeled native controls.
- **Do** keep the primary action visually clear within each workflow.
- **Do** keep provenance and limitations beside the results they qualify.
- **Do** verify desktop and narrow-screen form behavior after layout changes.

### Don't:

- **Don't** introduce custom HTML, CSS, or JavaScript into the Python application.
- **Don't** invent font, radius, spacing, motion, or breakpoint tokens from screenshots.
- **Don't** replace readable result text with color-only feedback.
