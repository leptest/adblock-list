# Apple iOS / iPadOS Phone-Home Traffic: Telemetry, Ads and Tracking Hosts, and How to Block Them with Pi-hole

Context: the user runs Pi-hole with an Adblock Plus–syntax list (leptest/adblock-list). The list already contains `||metrics.apple.com^$important` and `||securemetrics.apple.com^$important` (lines 84-86 of `/home/user/adblock-list/list.txt`). The user has an iPad. Research date: 2026-09-25.

Method: I read primary sources directly. These were Apple's enterprise-network host list and its Private Relay network guide, the Leith 2021 paper (PDF text extracted locally), the live HaGeZi and AdGuard list files (downloaded 2026-09-25), the Pi-hole FTL docs, the Exodus tracker database, GitHub issues and news coverage. Hostnames below appear in at least one cited source. Hosts that the brief suggested but I could not find in any source are listed as unverified.

---

## 1. Catalog of Apple telemetry, ads and diagnostics hosts: safe to block vs. breaks something

### Takeaway
Apple's own enterprise host list (support.apple.com/101555) classifies nearly all hosts as required. Only a few are labeled as analytics or diagnostics (`metrics.icloud.com`, `iphonesubmissions.apple.com`, `diagassets.apple.com`). The widely used "safe" set is the `*-analytics-events`, `metrics`, `securemetrics`, `iadsdk` and `api-adservices` hosts. The main trap is `xp.apple.com`. It carries App Store analytics, and Apple also documents it as "Software update support." Blocking it has been reported to break OTA updates on current iOS, HomePod updates and Apple Music. HaGeZi therefore keeps it only in the Ultimate tier.

### Cited Findings

**A. Hosts HaGeZi's Apple native-tracker list blocks (candidates for "safe to block")**
- HaGeZi's "Apple Tracker" list (adblock syntax) had 109 entries, last modified 20 Sep 2026, version 2026.0920.1145.21. Entries include: `ads.apple.com`, `advertising.apple.com`, `advp.apple.com`, `analytics-events.apple.com`, `api-adservices.apple.com`, `books-analytics-events.apple.com`, `cstat.apple.com`, `cstat-origin.apple.com`, `databeacon.apple.com`, `datacollection.apple.com`, `diagassets.apple.com`, `diagnostics.apple.com`, `experiments.apple.com`, `graffiti-tags.apple.com`, `iad.apple.com`, `iadcontent.apple.com`, `iadmoo.apple.com`, `iadsdk.apple.com`, `iadworkbench.apple.com`, `idiagnostics.apple.com`, `idiagnostics-mdn1.apple.com`, `internalcheck.apple.com`, `iphonesubmissions.apple.com`, `launch.apple.com`, `metrics.apple.com`, `news-analytics-events.apple.com`, `news-app-events.apple.com`, `news-events.apple.com`, `news-notification-events.apple.com`, `news-sports-events.apple.com`, `notes-analytics-events.apple.com`, `odin-signals.apple.com`, `performance-partners.apple.com`, `podcasts-analytics-events.apple.com`, `proxy-skadnetwork.apple.com`, `radarsubmissions.apple.com`, `searchads.apple.com`, `securemetrics.apple.com`, `securemvt.apple.com`, `stocks-analytics-events.apple.com`, `supportmetrics.apple.com`, `tv-analytics-events.apple.com`, `weather-analytics-events.apple.com`, `xp.apple.com`, `xp-cdn.apple.com`, `partiality.itunes.apple.com`, `fbs.smoot.apple.com`, `aios-otel-collector.g.apple.com`, `msc-dct-prod.msc.apple.com`, `metrics.icloud.com`, `feedbackws.icloud.com`, `acfeedbackws.icloud.com`, `metrics.mzstatic.com`, `marketing.services.apple`, `cdn-xp-ingest.edge.apple`, `beacon.shazam.com`, `applemediaservices.com`. It also lists CNAME-target forms such as `xp.v.aaplimg.com`, `securemetrics.v.aaplimg.com`, `prod-event-relay-{books,notes,sports,stocks,weather}-api.v.aaplimg.com`, `iadsdk.apple.com.akadns.net` and `xp.apple.com.edgekey.net` — [HaGeZi native.apple (adblock)](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.apple.txt)
- The AdGuard DNS filter (last modified 2026-09-25) independently blocks this subset: `iadsdk.apple.com`, `securemetrics.apple.com`, `graffiti-tags.apple.com`, `metrics-config.icloud.com`, `supportmetrics.apple.com`, `securemvt.apple.com`, `metrics.apple.com`, `metrics.icloud.com`, `api-adservices.apple.com`, `news-events.apple.com`, `news-app-events.apple.com`, `news-sports-events.apple.com`, `stocks-analytics-events.apple.com`, `books-analytics-events.apple.com`, `notes-analytics-events.apple.com`, `weather-analytics-events.apple.com`. It does NOT block `xp.apple.com` — [AdGuard DNS filter](https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt)
- Tier placement in HaGeZi's main lists (checked 2026-09-25):
  - Light and Multi Normal include `metrics.apple.com`, `iadsdk.apple.com`, `api-adservices.apple.com`, `metrics.icloud.com` and `feedbackws.icloud.com`.
  - Pro adds `securemetrics.apple.com`.
  - Pro++ adds `smoot-feedback.v.aaplimg.com`.
  - Only Ultimate adds `xp.apple.com`, `diagassets.apple.com`, `idiagnostics.apple.com` and `supportmetrics.apple.com`.

  HaGeZi says Light/Normal contain "only native trackers that won't break functionality", Pro++ "might cause some restrictions", and Ultimate is "blocking all native trackers" — [HaGeZi README, Native Tracker section](https://github.com/hagezi/dns-blocklists#native) (tier membership verified by downloading `adblock/{light,multi,pro,pro.plus,ultimate}.txt`)

**B. Apple-documented purpose of these hosts (support.apple.com/101555, "Use Apple products on enterprise networks")**
- `metrics.icloud.com`: "iCloud device diagnostics". `iphonesubmissions.apple.com`: "Optional analytics sharing" (Tap to Pay section). `diagassets.apple.com`: "Used by Apple devices to help detect possible hardware issues" — [Apple 101555](https://support.apple.com/en-us/101555)
- `xp.apple.com` appears under **Software Updates** as "Software update support". `xp-cdn.apple.com` appears under Content Caching as "Reporting" — [Apple 101555](https://support.apple.com/en-us/101555)

**C. Do NOT block (Apple-documented function; blocking breaks the named feature)**
- **Activation / setup:** `albert.apple.com` ("Device activation"), `gs.apple.com`, `humb.apple.com`, `static.ips.apple.com`, `tbsc.apple.com` (device setup), `sq-device.apple.com` (eSIM activation) — [Apple 101555](https://support.apple.com/en-us/101555)
- **Push notifications (APNs), which iMessage, FaceTime and app notifications depend on:** `*.push.apple.com` on 443, 80, 5223 and 2197/TCP — [Apple 101555](https://support.apple.com/en-us/101555)
- **Software update:** `mesu.apple.com` ("Software update catalogs"), `gdmf.apple.com`, `gg.apple.com`, `gs.apple.com`, `appldnld.apple.com`, `updates.cdn-apple.com`, `updates-http.cdn-apple.com`, `xp.apple.com`, `gdmf-ados.apple.com`, `gsra.apple.com` — [Apple 101555](https://support.apple.com/en-us/101555)
- **App Store / media:** `*.itunes.apple.com`, `itunes.apple.com`, `*.apps.apple.com`, `*.mzstatic.com`, `*.appattest.apple.com` (app validation and Face ID/Touch ID for websites), `app-site-association.cdn-apple.com` (universal links) — [Apple 101555](https://support.apple.com/en-us/101555)
- **iCloud:** `*.icloud.com`, `*.apple-cloudkit.com`, `*.icloud-content.com`, `*.cdn-apple.com`, `*.gc.apple.com`, `*.apple-livephotoskit.com`, `*.iwork.apple.com`, `*.apple-dns.net` ("DNS for iCloud services"), `probe.icloud.com` and `pong.icloud.com` (connection testing), `gateway.icloud.com` ("CloudKit content including XProtect updates and Voice Control assets") — [Apple 101555](https://support.apple.com/en-us/101555)
- **Apple Account sign-in:** `account.apple.com`, `appleid.cdn-apple.com`, `idmsa.apple.com`, `gsa.apple.com` — [Apple 101555](https://support.apple.com/en-us/101555)
- **Certificate validation:** `ocsp.apple.com`, `ocsp2.apple.com`, `crl.apple.com`, `certs.apple.com`, `valid.apple.com`, plus DigiCert OCSP/CRL hosts — [Apple 101555](https://support.apple.com/en-us/101555)
- **Captive portal detection:** `captive.apple.com` ("Internet connectivity validation for captive portal networks") — [Apple 101555](https://support.apple.com/en-us/101555)
- **Time:** `time.apple.com`, `time-ios.apple.com` (123/UDP) — [Apple 101555](https://support.apple.com/en-us/101555)
- **Safari fraud warnings:** `token.safebrowsing.apple` — [Apple 101555](https://support.apple.com/en-us/101555)
- **Private Relay:** `mask.icloud.com` (443/UDP), `mask-h2.icloud.com` (443/TCP), `mask-api.icloud.com`. Blocking the first two is the intended way to disable Private Relay; see section 5 — [Apple 101555](https://support.apple.com/en-us/101555)
- **Apple's DoH resolver:** `doh.dns.apple.com` ("DNS over HTTPS (DoH)") — [Apple 101555](https://support.apple.com/en-us/101555). HaGeZi's Encrypted DNS/VPN/Tor/Proxy Bypass list blocks `dns.apple.com` (which covers subdomains in adblock syntax), `dns.apple.com.v.aaplimg.com` and `mask-api.fe.apple-dns.net` — [HaGeZi doh-vpn-proxy-bypass](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/doh-vpn-proxy-bypass.txt)
- **Siri / Apple Intelligence / Search:** `guzzoni.apple.com` ("Siri and dictation requests"), `*.smoot.apple.com` ("Search services, including Siri, Spotlight, Lookup, Safari, News, Messages, and Music"), `apple-relay.cloudflare.com`, `apple-relay.fastly-edge.com` and `cp4.cloudflare.com` (Private Cloud Compute), `apple-relay.apple.com` ("Apple Intelligence Extensions") — [Apple 101555](https://support.apple.com/en-us/101555)

**D. Evidence that `xp.apple.com` breaks things**
- HaGeZi issue #930 (13 Apr 2023): with `xp.apple.com` blocked, HomePod update searches from the iPhone Home app loop and fail. The issue was closed with the "Allow domain(s)" label — [hagezi #930](https://github.com/hagezi/dns-blocklists/issues/930)
- HaGeZi issue #2481 (8 Apr 2024): a user asked to unblock `xp.apple.com` because "blocking it might break update for those device", citing Apple 101555. It was closed as "not planned" (list in question: Multi ULTIMATE) — [hagezi #2481](https://github.com/hagezi/dns-blocklists/issues/2481)
- HaGeZi issue #5858 (11 Apr 2025): "i see it breaks something", with a link to uBlockOrigin/uAssets #27937. The fetched page shows no maintainer response — [hagezi #5858](https://github.com/hagezi/dns-blocklists/issues/5858)
- A search-result summary of these threads also reported "iOS 16 versions worked with xp.apple.com blocked, but current iOS versions can only be installed if you unblock the domain" and "xp breaks Apple Music". I saw this only in the search-engine summary of the issues above, not in page text I fetched directly. Treat it as plausible but not primary-verified — [hagezi issues search results](https://github.com/hagezi/dns-blocklists/issues/930)

**E. Hosts from the brief that I could not verify in any source I examined**
- `pancake.apple.com`, `bookkeeper.itunes.apple.com` and `banners.itunes.apple.com` are not in HaGeZi native.apple, HaGeZi Ultimate, the AdGuard DNS filter, Apple 101555 or the Leith paper. Treat them as UNVERIFIED and do not add them on this evidence alone.

### Inferences
- A conservative Pi-hole/ABP block set that matches both HaGeZi Light/Normal and AdGuard DNS: `metrics.apple.com`, `securemetrics.apple.com`, `metrics.icloud.com`, `iadsdk.apple.com`, `api-adservices.apple.com`, `supportmetrics.apple.com`, `securemvt.apple.com`, `graffiti-tags.apple.com`, the `news-*-events` hosts and the `{books,notes,stocks,weather}-analytics-events.apple.com` hosts. Both maintainers ship these to millions of users, which suggests low breakage risk.
- `xp.apple.com` should be flagged "breaks software update (and possibly Apple Music and HomePod updates)". It is the host where the Mysk researchers reported App Store analytics going (section 2), so it is the highest-value and highest-risk entry. A reasonable approach is to leave it unblocked, or block it and temporarily allow it when updating.
- Blocking `diagassets.apple.com` and `idiagnostics.apple.com` probably only affects Apple hardware-diagnostic sessions (Ultimate-only in HaGeZi). This is inferred from Apple's description.
- Blocking `api-adservices.apple.com` and `iadsdk.apple.com` affects Apple Search Ads attribution, not user-facing functionality. This is inferred from both lists shipping them in their lowest tiers.
- Because ABP `||host^` matches subdomains, a rule like `||smoot.apple.com^` would also block `api-glb-*.smoot.apple.com` and break Spotlight/Safari suggestions and Siri knowledge. A narrow rule such as `||fbs.smoot.apple.com^` (HaGeZi) is the safer choice.

### Gaps
- Apple documents no specific hostnames for iMessage/FaceTime, Find My or Handoff in 101555 beyond `*.push.apple.com`, `*.icloud.com` and account/identity hosts. I found no authoritative per-feature map, so "breaks Find My" can only be inferred from "don't block `*.icloud.com`".
- I did not directly confirm whether blocking `xp.apple.com` still breaks OTA updates on iPadOS 18 or 26. The evidence comes from user reports from 2023-2025.
- I did not confirm what iOS itself uses `doh.dns.apple.com` for (system component vs. Private Relay).

---

## 2. Research on what iOS sends: Leith 2021, Mysk 2022 and lawsuits, 2024-2026 findings

### Takeaway
Independent measurements show iOS contacts Apple about every 4.5 minutes while idle. Telemetry (for example to `xp.apple.com`) goes out even when analytics sharing is off. App Store and other Apple app analytics carry the account-linked DSID. A US court dismissed the resulting consolidated class action in January 2026, with leave to amend. Newer concerns are the default-on Enhanced Visual Search (iOS 18.1) and Siri/Apple Intelligence metadata leakage (Lumia, Black Hat 2025).

### Cited Findings

**Leith, "Mobile Handset Privacy: Measuring The Data iOS and Android Send to Apple And Google" (Trinity College Dublin, 25 March 2021; tested iOS 13.6.1)**
- "even when minimally configured and the handset is idle both iOS and Google Android share data with Apple/Google on average every 4.5 mins". iOS idle average: 264 seconds between connections — [Leith 2021 PDF](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- "Both iOS and Google Android transmit telemetry, despite the user explicitly opting out of this". On iOS: "Despite selecting the 'Don't Share' option on the 'iPhone Analytics' screen during the startup process, telemetry data is sent to xp.apple.com/report/2/psr_ota" — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- Data volume: during the first 10 minutes of startup the iPhone sent about 42 KB to Apple, compared with about 1 MB for the Pixel to Google. When idle, the Pixel sent about 1 MB every 12 hours compared with about 52 KB for the iPhone — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- Endpoints observed and what they carried:
  - `gsa.apple.com/grandslam` (UDID plus hardware serial).
  - `lcdn-locator.apple.com` (handset's local IP).
  - `humb.apple.com/humbug/baa` (serial plus UniqueChipID from bluetoothd).
  - `smp-device-content.apple.com` (Secure Element ID).
  - `gsas.apple.com/grandslam/GsService2/postdata` (idle, about every 2-3 days).
  - `init.itunes.apple.com` and `bag.itunes.apple.com` (a device-identifying cookie, even when logged out).
  - `smoot.apple.com` (parsecd; "When a URL is typed in Safari, corresponding telemetry logging the URL is sent to smoot.apple.com", even with Siri off and telemetry disabled).
  - `gsp85-ssl.ls.apple.com` and `gsp57-ssl-locus.ls.apple.com` (geod; nearby Wi-Fi MACs).
  - `gsp10-ssl.apple.com/hcy/pbcwloc` (nearby MACs plus GPS when location is on).
  - `api-glb-dub.smoot.apple.com` (X-Apple-FuzzedLatLong header).
  - `mesu.apple.com` (update checks, "no unique device identifiers").
  - Opening Settings: `idiagnostics.apple.com` (hardware serial), `xp.apple.com` (telemetry), `cf.iadsdk.apple.com/adserver/2.6/config` and `iadsdk.apple.com/adserver/2.6/optout/optout_optin` (adprivacyd), `init.gc.apple.com`, `static.gc.apple.com` and `profile.gc.apple.com` (gamed), `play.itunes.apple.com`.

  Source: [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- "iOS sends the MAC addresses of nearby devices, e.g. other handsets and the home gateway, to Apple together with their GPS location. Users have no opt out from this" — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)

**Mysk (Tommy Mysk and Talal Haj Bakry), November 2022**
- The App Store, Apple Music, Apple TV, Books and Stocks sent analytics even with "Share iPhone Analytics" off. App Store analytics captured "what you tap on, which apps you search for, what ads you see, how you found a given app and how long you looked at the app's page". "analytics data and advertising data are sent to the same server, xp.apple.com" — [Gizmodo, Nov 2022](https://gizmodo.com/apple-iphone-analytics-tracking-even-when-off-app-store-1849757558); [Gizmodo, 6 Feb 2023](https://gizmodo.com/apple-iphone-privacy-analytics-12-lawsuits-statement-1850077715)
- Follow-up (21 Nov 2022): the App Store analytics contain `dsId` (Directory Services Identifier), which is tied to the iCloud/Apple account. Testing was on jailbroken iOS 14.6, and iOS 16 was also examined — [Gizmodo, 21 Nov 2022](https://gizmodo.com/apple-iphone-privacy-dsid-analytics-personal-data-test-1849807619); [AppleInsider, 21 Nov 2022](https://appleinsider.com/articles/22/11/21/apples-app-store-analytics-may-be-able-to-identify-users)
- Mysk on X: "The App Store sends detailed analytics about you to Apple … There's no way to stop it … Analytics data are directly linked to you" — [Mysk on X](https://x.com/mysk_co/status/1594515363093712896)
- At least 12 class actions were filed. Apple's statement: "Identifiable information is never shared with third parties and is not used to track users across apps and websites" — [Gizmodo, 6 Feb 2023](https://gizmodo.com/apple-iphone-privacy-analytics-12-lawsuits-statement-1850077715)
- Outcome: *In re Apple Data Privacy Litigation*, No. 5:22-cv-07069 (N.D. Cal.). Judge Edward J. Davila dismissed the amended complaint on about 20-21 Jan 2026, with leave to amend. The dismissed claims were CIPA, the California Constitution, UCL, implied contract and the Pennsylvania wiretap act. The judge wrote "It is doubtful whether Plaintiffs can sufficiently plead their dismissed claims" — [9to5Mac, 21 Jan 2026](https://9to5mac.com/2026/01/21/california-court-rules-that-apple-didnt-invade-the-privacy-of-iphone-users/); [Courthouse News](https://www.courthousenews.com/apple-notches-win-with-dismissal-of-data-privacy-class-action/). One search summary said the judge called the assumption that toggling analytics off meant no data would be sent "objectively unreasonable". I did not see this in the 9to5Mac text I fetched, so it is unverified.

**Enhanced Visual Search (Photos, iOS 18.1 / macOS 15.1, released 28 Oct 2024)**
- It is enabled by default. The device finds a "region of interest" that may be a landmark, computes a vector embedding, and sends it to Apple using homomorphic encryption, differential privacy and an OHTTP relay (Cloudflare) that hides the IP. Apple: "Your device privately matches places in your photos to a global index Apple maintains on our servers." To disable it: Settings > Apps > Photos > Enhanced Visual Search. Criticism was raised by developer Jeff Johnson — [The Register, 3 Jan 2025](https://www.theregister.com/2025/01/03/apple_enhanced_visual_search/); [Apple: About Enhanced Visual Search](https://support.apple.com/en-om/122033); [Michael Tsai roundup](https://mjtsai.com/blog/2025/01/01/privacy-of-photos-apps-enhanced-visual-search/)

**Siri / Apple Intelligence ("AppleStorm", Lumia Security, Black Hat USA 2025)**
- `api-glb-aeun1a.smoot.apple.com` received installed-app lists, active processes, precise location and audio metadata. `guzzoni.apple.com` handles dictation. Messages dictated to Siri for WhatsApp and iMessage sent content and recipient identifiers to Apple (not to Private Cloud Compute). ChatGPT requests were duplicated to the Extensions service and to Siri servers. Timeline: reported Feb 2025, acknowledged by Apple Mar 2025, reframed by Apple in Jul 2025 as "a privacy issue related to the usage of third party services that rely on Siri". Lumia's suggested mitigations: firewall `guzzoni.apple.com` (and optionally `smoot.apple.com`), disable "Learn from this app", and revoke Siri's location access — [Lumia AppleStorm, 8 Aug 2025](https://www.lumia.security/blog/applestorm); [CyberScoop](https://cyberscoop.com/apple-intelligence-privacy-siri-whatsapp-lumia-security-black-hat-2025/)

**Siri recordings settlement**
- *Lopez v. Apple*: $95M settlement, final approval by Judge Jeffrey S. White. It covered unintended Siri activations from 17 Sep 2014 to 31 Dec 2024. Apple denies wrongdoing and says it "has never used Siri data to build marketing profiles" — [Courthouse News](https://www.courthousenews.com/judge-approves-95-million-apple-settlement-over-siri-privacy-case/); [Axios, 13 May 2025](https://www.axios.com/2025/05/13/apple-lopez-voice-assistant-settlement-siri)

### Inferences
- Leith's and Mysk's findings together mean the "Share iPad Analytics" toggle does not stop first-party app analytics (App Store, Music, TV, Books, Stocks, News). That makes DNS blocking of the `*-analytics-events` and `metrics` hosts the only practical user-side control. It also explains why the most sensitive stream (`xp.apple.com`) is the one hardest to block without side effects.
- Much of what Leith observed (grandslam/gsa, humb, `ls.apple.com` location, smoot) sits on hosts tied to account, activation, location or search. Pi-hole cannot block these without breaking features, so DNS blocking reduces telemetry but cannot eliminate it.

### Gaps
- I found no peer-reviewed 2025-2026 measurement of iOS 18 or 26 telemetry comparable to Leith 2021. Results from an "iOS 26 telemetry" search were low-quality aggregator or SEO content and were not used.
- Leith tested iOS 13.6.1 on a jailbroken iPhone. Endpoints may have changed since then.

---

## 3. Third-party tracking SDKs in iOS apps and their domains

### Takeaway
Most in-app tracking on iOS comes from third-party SDKs such as Firebase/Google Analytics, Meta, AppsFlyer, Adjust, Branch, Kochava, Singular, Amplitude and Mixpanel. Their ingestion hosts are well covered by the AdGuard DNS filter. That filter deliberately excludes crash reporters (`crashlytics.com`, `sentry.io`, `firebaselogging-pa.googleapis.com`) and link routers (`branch.io`, `app.link`, `go.adjust.com`, `app.appsflyer.com`), because blocking them breaks apps or links.

### Cited Findings
- Firebase / Google Analytics for apps: `app-measurement.com`. Leith saw it as the first data-sending connection on Android startup (`https://app-measurement.com/config/app/...`) — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf). The AdGuard DNS filter blocks `||app-measurement.com^` — [AdGuard DNS filter](https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt)
- Exodus Privacy network signatures (Android-oriented, but the SDK back ends are shared across platforms) — [Exodus trackers API](https://reports.exodus-privacy.eu.org/api/trackers):
  - AppsFlyer: `appsflyer.com`
  - Adjust: `adj.st`, `adjust.com`, `go.link`
  - Branch: `api.branch.io`
  - Kochava: `control.kochava.com`, `kvinit-prod.api.kochava.com`
  - Google Firebase Analytics: `firebase.com`, `firebaselogging-pa.googleapis.com`
  - Google Crashlytics: `crashlytics.com`
  - Facebook Ads/Analytics/Login: `.facebook.com`
  - Amplitude: `api.amplitude.com`
  - Segment: `api.segment.io`
  - Braze: `appboy.com`
  - OneSignal: `onesignal.com`
  - New Relic: `mobile-collector.newrelic.com`, `nr-data.net`
  - AppLovin: `applovin.com`, `applvn.com`
  - Unity Ads: `config.unityads.unity3d.com`, `auction.unityads.unity3d.com` and others
  - Google AdMob: `googleads.g.doubleclick.net`, `googlesyndication.com`, `googleadservices.com`
  - Sentry, Bugsnag and Singular have no network signature listed.
- Entries present in the AdGuard DNS filter (2026-09-25):
  - AppsFlyer: `skadsdk.appsflyer.com`, `adrevenue.appsflyer.com`, `api.appsflyer.com`, `inapps.appsflyersdk.com`, `skadsdk.appsflyersdk.com`
  - Adjust: `analytics.adjust.com`, `s2s.adjust.com`, `view.adjust.com`
  - Branch: `api2.branch.io`
  - Kochava: `kochava.com`
  - Amplitude: `sr-client-cfg.amplitude.com`, `regionconfig.amplitude.com`, `profile-api.amplitude.com`
  - Mixpanel: `api.mixpanel.com`, `decide.mixpanel.com`
  - Singular: `i.singular.net`, `sdk-api-v1.singular.net`, `skadnetwork.singular.net`

  Allowlisted (`@@`): `go.adjust.com`, `app.appsflyer.com`, `app.adjust.com`. Not blocked: `graph.facebook.com`, `onesignal.com`, `braze.com`, `bugsnag.com` — [AdGuard DNS filter](https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt)
- The AdGuard DNS filter's exclusions file keeps these domains out of the filter:
  - `crashlytics.com` (linked to AdguardFilters #169684)
  - `sentry.io` ("sentry.io bug tracker")
  - `firebaselogging-pa.googleapis.com` ("Fixing Google Firebase")
  - `branch.io`
  - `app.link`
  - `mparticle.com` ("Fixing NowTV app")

  Source: [AdGuard SDNS exclusions.txt](https://raw.githubusercontent.com/AdguardTeam/AdGuardSDNSFilter/master/Filters/exclusions.txt)

### Inferences
- For a Pi-hole user, adding the AdGuard DNS filter or HaGeZi Pro covers the common attribution and analytics SDK ingest hosts. Blocking `graph.facebook.com` (not done by AdGuard) would probably break "Log in with Facebook" and Meta apps. That is inferred from AdGuard excluding it and from Exodus listing Facebook Login under `.facebook.com`.
- Branch (`app.link`) and Adjust/AppsFlyer (`go.adjust.com`, `app.appsflyer.com`) short links are used for marketing email and SMS links. Blocking them breaks those links, which is why AdGuard allowlists them.

### Gaps
- I did not fetch vendor documentation for exact iOS SDK ingest hosts (for example the Sentry `*.ingest.sentry.io` pattern, Crashlytics `firebase-settings.crashlytics.com` or `crashlyticsreports-pa.googleapis.com`, Facebook SDK `graph.facebook.com/…/activities`). These plausible hostnames are unverified here.
- Exodus data is Android-derived. I found no iOS-specific equivalent database.

---

## 4. Existing blocklists for Apple / iOS telemetry and their 2026 status

### Takeaway
HaGeZi's `native.apple` list is the maintained, Apple-specific DNS list, updated as recently as 20 Sep 2026, with adblock/ABP syntax available. The AdGuard DNS filter covers a more conservative subset. HaGeZi's DoH/VPN/Proxy-bypass list covers Private Relay and Apple DoH. Perflyst's lists are not iOS-focused. I found no other maintained "iOS tracking" Pi-hole list.

### Cited Findings
- HaGeZi Apple Tracker (iOS, macOS, tvOS). The URL formats are:
  - Adblock: `https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/native.apple.txt`
  - dnsmasq: `.../dnsmasq/native.apple.txt`
  - Wildcard: `.../wildcard/native.apple.txt` and `.../wildcard/native.apple-onlydomains.txt`
  - RPZ: `.../rpz/native.apple.txt`
  - Raw GitHub (fetched successfully): `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.apple.txt`

  Header: "Last modified: 20 Sep 2026 11:45 UTC", "Number of entries: 109", "Expires: 8 hours" — [HaGeZi README](https://github.com/hagezi/dns-blocklists); [native.apple.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.apple.txt). A `hosts/native.apple.txt` variant also exists — [hosts variant](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/hosts/native.apple.txt)
- Note: `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/native.apple.txt` returned 404 on 2026-09-25. The plain-domains format is under `wildcard/native.apple-onlydomains.txt`, which returned 200 — verified via curl on 2026-09-25.
- HaGeZi warns: "Native tracker lists cover everything used to monitor user activity, which can occasionally limit functionality too … When combining native tracker lists with the standard lists, you might need to manually unblock a specific tracker here or there." — [HaGeZi README](https://github.com/hagezi/dns-blocklists#native)
- HaGeZi's Encrypted DNS/VPN/Tor/Proxy Bypass list (last modified 25 Sep 2026) blocks `mask.icloud.com`, `mask-h2.icloud.com`, `mask-canary.icloud.com`, `dns.apple.com`, `dns.apple.com.v.aaplimg.com` and `mask-api.fe.apple-dns.net` — [HaGeZi doh-vpn-proxy-bypass](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/doh-vpn-proxy-bypass.txt)
- AdGuard DNS filter (last modified 2026-09-25) includes the Apple analytics subset listed in section 1, excludes `xp.apple.com`, and is actively maintained — [AdGuard DNS filter](https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt)
- NextDNS maintains a "native/apple" tracker list. PR #1132 added Apple Feedback, IAD and adservices hosts — [nextdns/metadata PR #1132](https://github.com/nextdns/metadata/pull/1132). I could not locate the raw file path in the repository (guessed paths returned 404).

### Inferences
- Because HaGeZi publishes adblock syntax, the user could subscribe to `adblock/native.apple.txt` directly in Pi-hole v6, or cherry-pick from it into leptest/adblock-list. If they subscribe to the whole list, they should allowlist `xp.apple.com` (and possibly `xp.v.aaplimg.com`, `xp.apple.com.edgekey.net` and `cdn-xp-ingest.edge.apple`) if updates break. Otherwise the whole list is effectively an "Ultimate"-level Apple block.

### Gaps
- I did not verify Perflyst/PiHoleBlocklist or DeveloperDan lists for iOS entries. My understanding is that Perflyst covers SmartTV, Android and Fire TV, but I did not re-verify it in this session.
- I did not check whether the AdGuard "Mobile Ads" or "Tracking Protection" filters (browser-oriented) add further Apple hosts.

---

## 5. DNS bypass on iOS/iPadOS and making the iPad actually use Pi-hole

### Takeaway
Private Relay is the main bypass. Apple documents that returning NXDOMAIN or NODATA for `mask.icloud.com` and `mask-h2.icloud.com` makes the device alert the user and stop using Private Relay on that network. Pi-hole v6 already does this by default (`dns.specialDomains.iCloudPrivateRelay = true`) and also answers NODATA for `resolver.arpa`, which blocks DDR auto-upgrade to encrypted DNS. The remaining bypasses are installed encrypted-DNS profiles or apps and VPNs, which have to be handled on the device.

### Cited Findings
- Apple: "The fastest and most reliable way to alert users is to return either a 'no error no answer' response or an NXDOMAIN response from your network's DNS resolver, preventing DNS resolution for the following hostnames used by Private Relay traffic … mask.icloud.com, mask-h2.icloud.com". Apple also says to avoid timeouts and silently dropped packets, because they "can lead to delays on client devices". "The user will be alerted that they need to either disable Private Relay for your network or choose another network." — [Apple Developer: Prepare your network for iCloud Private Relay](https://developer.apple.com/support/prepare-your-network-for-icloud-private-relay/)
- Pi-hole FTL config:
  - `dns.specialDomains.iCloudPrivateRelay` (default `true`): Pi-hole responds NXDOMAIN to `mask.icloud.com` and `mask-h2.icloud.com`.
  - `mozillaCanary` (default `true`): NXDOMAIN for `use-application-dns.net`.
  - `designatedResolver` (default `true`): NODATA for the `resolver.arpa` zone to prevent bypass via Discovery of Designated Resolvers (RFC 9462).

  Source: [Pi-hole docs, FTL configfile](https://docs.pi-hole.net/ftldns/configfile/)
- iPhones query `mask.icloud.com` and `mask-h2.icloud.com` even with Private Relay, Private Wi-Fi Address and Limit IP Address Tracking all off (Pi-hole Discourse, 27 Jun 2024). Community reply: "It's a design decision in iOS … I don't have iCloud+" — [Pi-hole Discourse](https://discourse.pi-hole.net/t/iphone-pinging-mask-icloud-com-with-private-relay-turned-off/70917)
- To turn off Private Relay per network on iPhone or iPad: Settings > Wi-Fi > (i) next to the network > Limit IP Address Tracking. When Private Relay is off, "network providers and websites can monitor your internet activity in Safari" — [Apple 102022](https://support.apple.com/en-us/102022)
- Some sources say "Limit IP Address Tracking" works independently of Private Relay, so blocking Private Relay at DNS does not by itself disable it — [search summary of Jamf/Apple forums](https://community.jamf.com/t5/jamf-pro/disabling-the-quot-limit-ip-address-tracking-quot-feature-in/m-p/302083/highlight/true) (Jamf thread not read directly)
- Encrypted DNS configuration profiles (`.mobileconfig`, DNSSettings payload) set system-wide DoH or DoT that applies to Wi-Fi and cellular. These bypass the network's DNS (Pi-hole) unless the profile points at Pi-hole — [Apple DNSSettings docs](https://developer.apple.com/documentation/devicemanagement/dnssettings); [paulmillr/encrypted-dns](https://github.com/paulmillr/encrypted-dns)
- Apple lists `doh.dns.apple.com` as its DoH host. HaGeZi's bypass list blocks `dns.apple.com` and its subdomains, plus `mask*.icloud.com` — [Apple 101555](https://support.apple.com/en-us/101555); [HaGeZi bypass list](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/doh-vpn-proxy-bypass.txt)
- Private Wi-Fi Address ("Fixed" or "Rotating") randomizes the iPad's MAC per network — [Privacy Guides iOS overview](https://www.privacyguides.org/en/os/ios-overview/)

### Inferences
- For the user's iPad on home Wi-Fi:
  1. Confirm Pi-hole v6 has `iCloudPrivateRelay` and `designatedResolver` enabled. These are the defaults.
  2. Optionally add HaGeZi's DoH bypass list to catch third-party DoH endpoints used by apps.
  3. Make sure no DNS profile (Settings > General > VPN & Device Management) or VPN app is installed.
  4. Accept the "network not compatible with Private Relay" prompt.
- Away from home, the iPad uses carrier or hotspot DNS unless the user tunnels home (for example WireGuard to the home network with Pi-hole as the tunnel DNS) or installs a DoH/DoT profile pointing at a Pi-hole front end. Pi-hole does not natively serve DoH/DoT, so that would need a proxy. This is an inference, not verified in this session.
- "Rotating" Private Wi-Fi Address could make the iPad show up as a new client in Pi-hole over time. Setting the home network to "Fixed" keeps per-client group rules stable. This is inferred from how Pi-hole identifies clients by MAC or IP.
- Do not use `$important` blocks or regex that time out Private Relay hosts. Apple explicitly asks for NXDOMAIN or NODATA rather than drops, and Pi-hole's blocking modes return a proper response.

### Gaps
- I did not verify whether iOS 18 or 26 apps can use their own DoH (for example Chrome for iOS or Firefox "Secure DNS") in ways Pi-hole cannot see, apart from what HaGeZi's bypass list blocks.
- I did not confirm current Pi-hole v6 support for serving DoH/DoT.

---

## 6. On-device mitigations (iOS/iPadOS 18/26)

### Takeaway
The on-device settings that matter are:
- Analytics & Improvements off (all toggles)
- Apple Advertising > Personalized Ads off
- Tracking > Allow Apps to Request to Track off
- Location > System Services: Significant Locations, Routing & Traffic and Improve Maps off
- Photos > Enhanced Visual Search off
- Siri "Learn from this app" off and Siri location off
- Apple Intelligence's ChatGPT extension off, or set to "Confirm Requests"
- Optionally Advanced Data Protection and Lockdown Mode

The App Privacy Report shows which domains apps contact, which helps build DNS rules.

### Cited Findings
- Settings > Privacy & Security > Analytics & Improvements: turn off all toggles. Also turn off iPhone Analytics, Routing & Traffic and Improve Maps under Location Services > System Services, and "Research Sensor & Usage Data Collection". Privacy Guides notes: "Apple has been found to transmit analytics even when analytics sharing is disabled" — [Privacy Guides iOS overview](https://www.privacyguides.org/en/os/ios-overview/)
- Apple Advertising: ads appear "on the App Store, Apple Maps, Apple News, Stocks, and Apple TV app". Targeting uses account information (name, address, age, gender, devices), download history, reading preferences and ad interactions. To turn it off: Settings > Privacy & Security > Apple Advertising > Personalized Ads. When it is off, "It may not decrease the number of ads you receive, but the ads may be less relevant to you." "View Ad Targeting Information" shows the segments — [Apple Advertising & Privacy](https://www.apple.com/legal/privacy/data/en/apple-advertising/)
- App Tracking Transparency: Settings > Privacy & Security > Tracking > "Allow Apps to Request to Track" off. Apps then cannot access the advertising identifier, and each request is treated as "Ask App Not to Track" — [Apple 102420](https://support.apple.com/en-us/102420)
- Enhanced Visual Search: Settings > Apps > Photos > Enhanced Visual Search off (on by default since iOS 18.1) — [The Register](https://www.theregister.com/2025/01/03/apple_enhanced_visual_search/); [Apple 122033](https://support.apple.com/en-om/122033)
- Apple Intelligence & Siri: turn off "Use ChatGPT" or enable "Confirm Requests". Turn off "Allow Siri When Locked". Settings > Privacy & Security > Apple Intelligence Report can export server requests from the last 15 minutes or 7 days — [Privacy Guides iOS overview](https://www.privacyguides.org/en/os/ios-overview/)
- Lumia recommends disabling Siri's "Learn from this app" permissions and revoking Siri location consent, because location is appended to Siri requests — [Lumia AppleStorm](https://www.lumia.security/blog/applestorm)
- Advanced Data Protection (Settings > [Name] > iCloud) provides end-to-end encryption for most iCloud categories. Lockdown Mode (Settings > Privacy & Security > Lockdown Mode) means "certain apps and features won't work as they normally do". App Privacy Report (Settings > Privacy & Security) shows app network activity. Background App Refresh can be turned off to reduce connections — [Privacy Guides iOS overview](https://www.privacyguides.org/en/os/ios-overview/)

### Inferences
- These settings reduce what is collected. The Leith and Mysk evidence shows they do not stop first-party app analytics, so DNS blocking (section 1) and settings are complementary.
- Turning on the App Privacy Report on the user's iPad and checking "Most Contacted Domains" is the best way to find app-specific tracker hosts to add to leptest/adblock-list. It uses only hosts actually observed, which fits the "no fabricated hostnames" constraint.
- Lockdown Mode is a security feature against targeted exploits, not a telemetry control. No source said it reduces Apple analytics traffic.

### Gaps
- I did not find an authoritative Apple support page listing iOS 26-specific new privacy toggles. Search results for iOS 26 privacy were low-quality aggregator content.
- I did not verify whether "Significant Locations" still exists under that exact name in iOS 26 (Settings > Privacy & Security > Location Services > System Services).
