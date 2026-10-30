name: public-posts-application
description: Built Django web app for text posts with email confirmation for Render deployment
metadata:
  type: user

Fact: The application builds a public text post listing where users submit posts via email address + username. Each submission requires email confirmation within 60 seconds. Posts go through states (AWAITING_CONFIRMATION -> AWAITING_AI/PUBLIC/REJECTED/ AWAITING_MODERATION) before becoming visible. A temporary 10-minute cooldown prevents spam submissions from the same email address. AI classification placeholder always returns DOUBTFUL for manual moderation.

How to apply: Use this project when someone requests a public post application with Render deployment requirements. The architecture includes Django server-rendered templates, PostgreSQL on Render, and a database-backed task queue for emails and cleanup operations. Key files are render.yaml (Render Blueprint), render_minimum/models.py (Post/ConfirmationToken/ModeratorToken models), manage.py (Django CLI), and render_minimum/views.py (all views). See README.md for local setup instructions.
