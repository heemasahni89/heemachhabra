# PPT compliance matrix

Source: `website.pptx` (11 slides, 6 embedded media)

| # | PPT requirement | Current implementation | Status | Change required | Dependency |
|---|---|---|---|---|---|
| 1 | Brand `Heema Chhabra Design Consultant` / `HCDC` | H1, title, JSON-LD, OG use HCDC consistently; `HEEMA SAHNI` removed | PASS | — | — |
| 2 | `LOGO — HCDC` | SVG logo present, text updated to `HEEMA CHHABRA DESIGN CONSULTANT` | PASS | — | — |
| 3 | Intro imagery: paint / wood / stone / texture | Gallery exists but uses template portfolio screens; no material-led intro set | PARTIAL | Add material-led intro treatment on editorial pages; do not replace gallery without rights | Image 01 / verified material imagery |
| 4 | `Image 01 I have mailed you` (slide 4) | Not found in repo, PPT media, or `_nuxt/img`; no `Image 01` asset located | FAIL | Owner to supply Image 01 | **OWNER: Image 01** |
| 5 | `PUT PROJECT PICTURE` (slide 5) | Gallery retains 68 `screen*.jpg` + 14 hashed assets from template | PARTIAL | Classify provenance; replace only with verified HCDC photography | **OWNER: HCDC project photography** |
| 6 | Hero: `Spaces That Reflect Who You Are.` | Not present as hero line; About contains paraphrase | PARTIAL | Add hero line to home (without turning homepage into article) | — |
| 7 | `Quiet Luxury · Timeless Sophistication · Bespoke Craftsmanship · Personalised Design` | Not rendered; brief says use sparingly | PARTIAL | Add sparingly as secondary brand language | — |
| 8 | Intro: `Exceptional interiors are not created simply to be admired...` | About intro is truncated paraphrase | PARTIAL | Align to editorial source (section 7) | — |
| 9 | `Beauty With Purpose` + copy | About has `Beauty with Purpose` with paraphrased copy | PARTIAL | Align to section 7 wording | — |
| 10 | `Listen. Understand. Design. Refine.` + 6-stage approach | About has 6 stages but wording differs (`Design Development & Handover` vs `EXECUTE`) | PARTIAL | Align to section 7: Understand / Conceptualise / Curate / Detail / Execute / Experience | — |
| 11 | Residential: rooms list + scope (space planning, bespoke furniture, joinery, lighting, styling) | About includes residential summary but not full room list | PARTIAL | Expand to full service scope without implying inclusion | — |
| 12 | Private Residences: cohesive composition, character/comfort/longevity | Present in About as short paragraph | PASS | Keep concise | — |
| 13 | Commercial: identity/function/circulation/atmosphere/durability/user behaviour | About has paraphrase | PARTIAL | Align to section 7; remove unverified factory/complex claim | — |
| 14 | Builder/Development: show homes, common areas, palettes, guidelines | About has short builder paragraph | PARTIAL | Expand to explicit scope list | — |
| 15 | Founder: `Meet Heema Chhabra` — London studio, considered interiors | About intro mentions founder implicitly, no dedicated founder block | PARTIAL | Add founder section without invented credentials | — |
| 16 | Contact: `Start a Conversation`, London, appointment, `info@heemachhabra.com`, Instagram, no address/map/form | About has contact fragment; no dedicated contact route | PARTIAL | Create `/contact/` with verified contact only | — |
| 17 | Pinterest references (slide 3) | Not used as assets | PASS | Keep as references only; do not download as production images | — |

## Summary

PASS: 3 (brand/logo, Pinterest not used, private-residence intent)
PARTIAL: 11 (content present but not yet aligned to section 7 source)
FAIL: 1 (Image 01 missing) + gallery provenance unverified

No Pinterest, competitor, or hotlinked assets were added. Gallery remains on template screens until owner-approved photography is supplied; captions are intentionally blank rather than fabricated.
