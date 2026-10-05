---
target: v3 block
total_score: 28
max_score: 40
na_heuristics: 
p0_count: 1
p1_count: 2
target_identity: "file:/home/user/clod/where-to-buy/src/block-v3.html"
target_fingerprint: "sha256:2f74e1fcf21d5a0517665353440be4fe63a692d8895fff798d589264c24729ec"
target_path: /home/user/clod/where-to-buy/src/block-v3.html
timestamp: 2026-10-05T10-25-46Z
slug: where-to-buy-src-block-v3-html
---
Method: dual-agent (A: design review · B: detector + browser)

| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | System status | 2 | Mobile list tap scrolls to #rg-points (section top), map is below the open list, balloon opens off-screen |
| 2 | Real world | 3 | Raw address strings inconsistent (пр-т / пр-т., ул. only on some) |
| 3 | User control | 3 | No way back to "nearby" view after picking a city; denial note never clears |
| 4 | Consistency | 3 | Socials 3x in 3 styles; phone in two formats |
| 5 | Error prevention | 3 | Zero CTA leads to all venues though Zero is not everywhere |
| 6 | Recognition | 3 | 19-22 flat rows, map out of sight |
| 7 | Flexibility | 2 | No street/metro search, no grouping |
| 8 | Minimalism | 3 | Zero cans twice, socials 3x, contacts 2x |
| 9 | Error recovery | 3 | Geo-denied message doesn't say how to allow |
| 10 | Help | 3 | «Точка» never explained as a chain |
| Total | | 28/40 | Good |

Specificity: authored details (cans, metro badges in line colours, ZERO slab, Untappd) on a stock locator skeleton; no "which can are you holding" moment.
Detector: 11 static (9 broken-image, 2 cramped-padding) all false positives; overlay: clipped-overflow #rg-map (intentional), Yandex internals, column-overflow at 1440 (low). No contrast/target/overflow/console issues inside #rg-wtb.

Priority issues:
- [P0] List tap / geo result never shows the map on phone (scrollToMap targets #rg-points; grid order list→map). Fix: scroll to #rg-map and collapse list <900px, or map above list / sticky map. /impeccable layout
- [P1] Dead end outside Минск/Лида/Бобруйск: .rg-nopoint only offers Telegram; 110 partners hidden. Fix: link to partner list/v2. /impeccable clarify
- [P1] .rg-pitem__main aria-label overrides distance+metro for screen readers; chip count aria-label on span ignored; focus not moved to #rg-nearest after geo. /impeccable harden
- [P2] Popup actions .rg-pop a ~18px tall. Fix: 44px pill buttons. /impeccable adapt
- [P2] Lower page repetition (Zero cans twice, socials 3x, contacts 2x), FAB covers bottom content. /impeccable distill

Personas: Casey (list taps do nothing, tiny popup links, FAB overlap), Jordan («Точка» unexplained), Sam (aria-label hides distance), QR-scanner (no "this can" path, dead end outside 3 cities).
Minor: headbg 0.96 ghosting; faint is-active row; metro digits 10px; desktop list ends 60px above map; 66 tab stops in open list.
Questions: ask "which can?" first; phone: 3 nearest cards + map on demand; hide 110 partners or not.
