# Example: pipeline comparison on a one-off research question

**Date:** 2026-08-06
**Question:** What is causing the chorki.com website to not play videos?

Run side by side to compare two research pipelines on the same question:

1. **This repo's `web` skill**, chained behind the local `web-crawler` (one
   instance per cause-category: technical/user-side, and business/legal/news)
   and `web-consolidator` skills.
2. A separate third-party plugin (`web@web-plugin`,
   https://github.com/taliskerpruighe/web-plugin), run headless via
   `claude -p --agent web:web-main "/web:web <question>"`.

Both landed on the same core finding — a June 2026 U.S. federal contempt
order against Chorki's owner, Mediastar Limited, ordering the chorki.com
domain transferred and the Chorki apps pulled from the Google and Apple app
stores — with the same caveat that neither source confirms whether that
order has actually been executed yet, so the link to today's playback
failure is an inference, not a stated fact.

The `web-crawler`/`web-consolidator`/`web` chain did more digging (two
full category sweeps, each re-searched until results stabilized) and
additionally surfaced the underlying data-privacy lawsuit (VPPA claims) and
a list of ordinary technical fixes (buffering, iOS crashes, cache/extension
conflicts, geo-blocking). The plugin ran a leaner, fixed two-query sweep and
came back faster but thinner.

---

## Answer A — this repo's pipeline (web-crawler x2 → web-consolidator → web)

**I flag a court order as the likely cause, not a technical glitch.** A
federal lawsuit — *Hossain et al. v. Mediastar Limited* (Chorki's owner),
filed Feb 2024 in the Southern District of New York over alleged misuse of
subscriber data — reached a contempt ruling in June 2026. The court ordered
the chorki.com domain transferred away from Mediastar and directed Google
and Apple to pull the Chorki apps from their stores.
([Justia docket](https://docs.justia.com/cases/federal/district-courts/new-york/nysdce/1:24-cv-01201/615838/114),
[Wikipedia](https://en.wikipedia.org/wiki/Chorki))

**I can't confirm the order has actually been carried out.** Neither source
says whether the domain handover or app-store removal has happened yet.
Today is Aug 6, 2026 — after the June order — so it's plausible it's
already in effect, but that's an inference connecting the dates, not
something either source states outright.

**If it's not that, here are the ordinary fixes to rule out.** Chorki's own
FAQ and user reports point to buffering, iOS crashes, cache/extension
conflicts, and geo-blocked content as known causes, with fixes: update the
app, clear cache, check your connection, or email support@chorki.net.
([Chorki FAQ](https://www.chorki.com/page/faq),
[JustUseApp reports](https://justuseapp.com/en/app/1543140698/chorki/problems),
[Chrome help](https://support.google.com/chrome/answer/6138475?hl=en))

**Gap:** nobody could reach Chorki's FAQ page directly during this search to
check for an official outage notice.

## Answer B — the third-party plugin (`/web:web`, headless)

Here's what the sweep found on why chorki.com isn't playing videos:

### Direct answer

The most specific and recent explanation found is a legal one, not a
technical glitch: Wikipedia's "Legal proceedings" section (updated
2026-08-06) states that in June 2026 the U.S. District Court for the
Southern District of New York issued a contempt order against Mediastar
Limited (Chorki's owner) for violating a prior preliminary injunction, and
ordered the chorki.com domain name transferred to the plaintiffs' counsel —
while also directing Google and Apple to remove the Chorki mobile apps from
their app stores. If that domain transfer/app-removal order has been
carried out, that would directly explain why chorki.com isn't playing
videos right now. This is the only source that speaks to Chorki
specifically with a dated, current cause.

No other source found describes an actual outage or malfunction specific to
Chorki today — the rest offer only generic browser troubleshooting causes
that don't mention Chorki by name.

### Supporting findings

- Chorki is a Bangladeshi subscription streaming platform owned by Transcom
  Group via Prothom Alo/Mediastar Limited, primary URL chorki.net (also
  operates chorki.com), launched 12 July 2021.
- The Chorki Android app (via Google Play) was last updated Jul 30, 2026 and
  is still listed as available (3.1 stars), but links to chorki.net rather
  than chorki.com.
- Common general reasons a site's videos fail in Chrome: outdated browser,
  disabled JavaScript, too many open tabs, network/ISP issues.

### Gap flagged by the plugin itself

No source directly confirms, with a timestamp near today, that chorki.com is
currently down or shows a specific error. The legal domain-transfer order is
the strongest lead because it's Chorki-specific and dated this year, but the
article doesn't say whether the transfer/app removal has actually been
executed yet. Six pages could not be read, including Chorki's own FAQ page —
the same gap Answer A hit.
