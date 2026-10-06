---
target: v3 block
total_score: 31
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 2
target_identity: "file:/home/user/clod/where-to-buy/src/block-v3.html"
target_fingerprint: "sha256:0a64d20b5eab79f6900209ae13ed0b1b439daf38fc288d0d06effaf3c74778f2"
target_path: /home/user/clod/where-to-buy/src/block-v3.html
timestamp: 2026-10-06T09-32-21Z
slug: where-to-buy-src-block-v3-html
---
Method: dual-agent (A: design review · B: detector + browser)

| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | System status | 3 | Geo-denied note stays in hero after auto-scroll, hidden under header |
| 2 | Real world | 4 | Metro, districts, prepositional labels |
| 3 | User control | 3 | Geo replaces city/district silently |
| 4 | Consistency | 3 | Address formats vary; popup text links vs list icon buttons |
| 5 | Error prevention | 3 | Zero CTA leads to all venues |
| 6 | Recognition | 3 | List collapsed on mobile behind select-like toggle |
| 7 | Flexibility | 3 | FAB good; no search |
| 8 | Minimalism | 3 | Instagram x3, phone/email x2, marquee decorative |
| 9 | Error recovery | 3 | Recovery good, message lost |
| 10 | Help | 3 | Hints good |
| Total | | 31/40 | Good |

Detector: 22 static (10 broken-image, 9 buried-raster, 3 cramped-padding) all false positives/intentional; overlay 4 (clip on #rg-wtb/#rg-map, ymaps x2) intentional/third-party. Measured: inline contact links 41px tall; gesture hint 4.40:1.

Priority:
- [P1] Balloon actions .rg-pop a ~18px tall -> 44px buttons. adapt
- [P1] .rg-pitem__main aria-label hides distance/metro -> visually-hidden prefix. harden
- [P2] #rg-geo-note invisible after scroll -> show in #rg-points. clarify
- [P2] Hero photo shows discontinued Vista, aria-label names it. (asset)
- [P3] Contact duplication (Instagram x3, phone x2), list collapsed on mobile. distill
Minor: "Ищите в точках" lowercase; desktop scroll offset; Zero Stout low-count rating; inline links 41px; gesture hint contrast 4.40.
