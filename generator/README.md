# Social post generator

Renders Harman's branded 1080×1350 posts (Instagram portrait, also fine for Facebook) from a JSON file.

    python3 gen/build.py gen/posts-2026-10.json ../2026-10

- Templates: `stats_region`, `stats_city` (with buyer/balanced/seller gauge), `insight`, `brand`, `listing`.
- Each run writes one PNG per post plus `captions.md` with the caption and suggested posting date.
- Needs Chromium (`/opt/pw-browsers/...` in Claude's environment) and Pillow. Inter font must be installed; Playfair Display is bundled in `assets/`.
- Monthly data source: Fraser Valley Real Estate Board monthly + municipal reports (Surrey, Langley, North Delta). The municipal page does not show +/- direction on % changes, so city posts use benchmark prices and counts only.
