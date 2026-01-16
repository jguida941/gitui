# ADR-0009: Visualization Library for Graphs

Status: accepted

Context
- We want charts (activity, churn, author stats) and a commit graph view.
- The UI is Qt-based, so the library must integrate with Qt widgets cleanly.
- We prefer minimal dependencies and good performance for large repos.

Decision
- Use PyQtGraph for charts (time series and bar charts).
- Use QGraphicsView for the commit DAG (custom lanes + edges).
- Data comes from git CLI outputs parsed into models; no direct libgit usage.
- Add PyQtGraph to runtime dependencies when Phase 2.5 starts.

Consequences
- We introduce a new dependency (PyQtGraph) once graphs are implemented.
- Commit graph rendering remains custom (no third-party graph widget).
- Tests must validate data aggregation so charts match CLI totals.
