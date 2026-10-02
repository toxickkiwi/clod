# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Tilda. Live site robimgood.beer is built on Tilda; new or reworked page sections ship as self-contained HTML/CSS/JS pasted into a Tilda HTML block (T123). The rest of the site, including Tilda's own header menu and footer, stays as is. `site/` holds a static recreation of /mestaprodazh (template.html + data.json + build.py → index.html) used as the working copy; `site-source/` keeps the original Tilda HTML and screenshots for reference.

## Users

Beer buyers in Belarus. They come to the site to find out where to buy Robim Good cans near them and to learn about the beers. Many arrive on a phone, often when they are already out and about (confirmed: primary audience is the consumer, not trade buyers).

## Product Purpose

Robim Good Brewery is a Belarusian brewery selling canned beer through its own partner retail network. The site tells people what the beers are, where to buy them, and what else the brewery offers (tours, catering). Success for the "Места продаж ж/б" page: a visitor quickly finds a nearby shop or bar that stocks the cans.

## Positioning

Confirmed differentiators, all true at once:
- Unusual styles, e.g. FACTORY TOMATO BBQ, a tomato sour.
- A dedicated non-alcoholic line: Zero IPA and Zero Lager.
- Its own brewery that people can visit: beer excursions and catering ("Пиво на природе").
- Wide distribution: 22 «Точка» shops and bars plus 110 partner venues across Minsk and six regions.

## Operating Context

Visitors use the site to plan a purchase: check which venue near them stocks the cans, call ahead, go there. The main retail partner is the «Точка» chain of shops and bars. Partner venues are a mix of shops, bars, pubs, cafés and restaurants.

## Capabilities and Constraints

- Canned range shown on the hero (figures from the can labels: ABV / IBU / original gravity):
  - FACTORY I.P.A Vista, American IPA: 6.3% / 65 IBU / 16%
  - FACTORY TOMATO BBQ, Tomato Sour: 5.1% / 0 IBU / 16.5%
  - Zero Lager, non-alcoholic: 0% / 20 IBU / 7%
  - Zero IPA, non-alcoholic: 0% / 40 IBU / 7.5%
- Venue data lives in `site/data.json`: «Точка» entries (type, city, address, phone) and partners grouped by region (name, address). Partner entries have no phone numbers.
- Delivery constraint: output must work inside a Tilda T123 HTML block. Styles must be scoped so they don't clash with Tilda's CSS. No build step on Tilda's side. Tilda's header and footer are not part of the deliverable.
- Site language: Russian.
- Undecided: whether stock differs between venues (which beer is available where); opening hours; map coordinates.

## Brand Commitments

- Name: Robim Good Brewery. Logo: "Robim / good / BREWERY" wordmark (`site/img/logo.png`).
- The can photography (four cans flying against a blue sky) is the current hero asset.
- Font on the live site: Fira Sans Condensed.

## Evidence on Hand

- Hero photos: `site/img/hero.jpg`, `site/img/hero-alt.jpg`. Footer texture: `site/img/footer.jpg`.
- Full venue list: `site/data.json` (22 «Точка» + 110 partners in 7 regions).
- Contacts: +375 29 661-17-01 (also Telegram/Viber), info@robimgood.beer, Facebook and Instagram @robimgoodbrewery.
- Absent, never fabricate: customer reviews, ratings, sales figures, awards, prices, per-venue stock, opening hours, map coordinates.

## Product Principles

- Getting the buyer to a can is the job. Every page should shorten the path from "I want this beer" to "I know where to get it nearby".
- The beers are the heroes. Unusual flavours and the Zero line are the story; show the product itself, not generic beer imagery.
- Local and concrete. Real addresses, real phones, real cities, nothing vague.
- Phone first. Most visitors decide on the move.
