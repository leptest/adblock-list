# Android phone privacy: tracking, telemetry and phone-home traffic, and blocking it at DNS level with Pi-hole

Scope: Android 14/15/16-era phones (Google Play Services / GMS plus OEM skins), what they contact, what you can block with Pi-hole without breaking things, existing blocklists, DNS-bypass paths and on-device mitigations. Research date: 2026-09-25.

Method note: hostnames below come from (a) text I extracted from the Leith et al. PDFs (TCD/Edinburgh), (b) Google's Android Enterprise network-requirements page, (c) blocklists I downloaded on 2026-09-25 (HaGeZi native.* via jsDelivr, AdGuard filters 3 and 11, GoodbyeAds, Perflyst, Exodus API). I list no hostname that did not appear in one of those. "Status" means whether a DNS block is safe or what it breaks. Where breakage is my inference and not a reported result, it is marked **(inferred)**.

Existing coverage in the user's `list.txt` (checked with grep): `||doubleclick.net^` (so `googleads.g.doubleclick.net` and `securepubads.g.doubleclick.net` are already covered), Xiaomi `data.mistat.{,intl.,india.,rus.}xiaomi.com`, `sa.api.intl.miui.com`, `tracking.{intl,india,rus}.miui.com`; OnePlus `analytics.oneplus.cn`, `click.oneplus.com`; Samsung `ad.samsungadhub.com`, `samsungadhub.com`, `bigdata.ssp.samsung.com`.

---

## 1. Google / GMS telemetry: which domains are safe to block, and which break push, Play Store, updates or login

### Takeaway
Most GMS telemetry goes to the same hostnames that the Play Store, check-in and FCM use: `play.googleapis.com` (log/batch and play/log), `www.googleapis.com` (experimentsandconfigs) and `android.clients.google.com` (checkin). A DNS blocker cannot separate URL paths, so blocking those hostnames breaks core functions. The Google hosts you can block safely are the ad and analytics ones: `app-measurement.com`, `*.doubleclick.net`, `googleadservices.com`, `googlesyndication.com`, `adservice.google.*` and `ssl.google-analytics.com`, plus the Firebase/Crashlytics telemetry hosts. Never block `mtalk.google.com` (with its `alt*-mtalk` variants and ports 5228-5230), `fcm.googleapis.com`, `android.googleapis.com`, `accounts.google.com` or `connectivitycheck.gstatic.com`.

### Cited Findings

**What Leith measured (Pixel, Google Android)**
- Even when idle and minimally configured, Google Android on a Pixel contacts Google about every 255 s (≈ every 4.5 min). It sends about 1 MB to Google in the first 10 minutes after startup, and roughly 1 MB every 12 hours while idle (iPhone: 42 KB and 52 KB). This holds with Settings > Google > Usage & Diagnostics turned off — [Leith, "Mobile Handset Privacy: Measuring the Data iOS and Android Send to Apple and Google" (2021)](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- With "Send usage and diagnostic data" deselected at setup, about 1.2 MB of telemetry still goes to `play.googleapis.com/log/batch` (Google Play Services) and `play.googleapis.com/play/log` (Play Store app), every 10-20 minutes. Another 1.1 MB of device data goes to `www.googleapis.com/experimentsandconfigs`, and 181 KB to `android.clients.google.com/checkin` — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- `android.clients.google.com/checkin` receives the Wi-Fi MAC address, hardware serial and IMEI, which links them together. A later check-in links these to the Google Android ID, a persistent ID that only changes with a factory reset. The same host is also used by the Firebase service (SafetyHub app) — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- The first data-bearing connection on startup is to the Google Analytics endpoint `app-measurement.com` (`/config/app/...` with `app_instance_id`). The app instance ID is later linked to the resettable advertising ID (RDID/AdID) — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- Other Google endpoints seen in the 2021 study: `ssl.google-analytics.com/batch` (Clock app); `www.googleadservices.com` (YouTube, sends the RDID); `youtubei.googleapis.com/youtubei/v1/logevent`; `growth-pa.googleapis.com` (GetPromos); `mobilenetworkscoring-pa.googleapis.com` (GetWifiQuality, purpose unclear); `firebaseinstallations.googleapis.com`; `android.googleapis.com` (connections about every 6 h) — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- Leith's 2025 cookies study (Pixel 7, Android 14 build AP4A.241205.013, GMS 24.47.38) found that shortly after Google sign-in, Play Services calls `googleads.g.doubleclick.net/pagead/drt/m`. That response sets a DSID advertising cookie on `.doubleclick.net`, which is stored in GMS data. This happens before the user opens any Google app. "No consent is sought for storing any of this data and there is no opt out." — [Leith, "Cookies, Identifiers and Other Data That Google Silently Stores on Android Handsets"](https://www.scss.tcd.ie/doug.leith/pubs/cookies_identifiers_and_other_data.pdf); published version in [Computers & Security (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S016740482600026X); press summaries: [TCD news](https://www.tcd.ie/news_events/articles/2025/google-cookies/), [The Register](https://www.theregister.com/security/2025/03/04/googles-consent-less-android-tracking-probed-by-academics/1220113)
- The same 2025 study saw the Play Store app send first_open and screen_view events together with `google_ad_id` and `firebase_instance_id` to Firebase Analytics at `region1.app-measurement.com/a`. It also saw Clearcut telemetry to `play.googleapis.com`, a cookie sent to the telemetry logger `play.google.com/log`, and ad-click tracking via `www.google.com/aclk` — [Leith 2025](https://www.scss.tcd.ie/doug.leith/pubs/cookies_identifiers_and_other_data.pdf)
- Many other GMS endpoints appear in the 2025 paper. Most are functional APIs, not pure telemetry: `play-fe.googleapis.com`, `playatoms-pa.googleapis.com`, `deviceintegritytokens-pa.googleapis.com`, `phonedeviceverification-pa.googleapis.com`, `locationhistory-pa.googleapis.com`, `semanticlocation-pa.googleapis.com`, `userlocation.googleapis.com`, `geller-pa.googleapis.com`, `nearbysharing-pa.googleapis.com`, `notifications-pa.googleapis.com`, `people-pa.googleapis.com`, `securitydomain-pa.googleapis.com`, `cryptauthenrollment.googleapis.com`, `cryptauthdevicesync.googleapis.com`, `android-context-data.googleapis.com`, `feedback-pa.googleapis.com`, `auditrecording-pa.googleapis.com`, `mobileconfiguration-pa.googleapis.com`, `gmscompliance-pa.googleapis.com`, `findmydevice-pa.googleapis.com`, `spot-pa.googleapis.com`, `discover-pa.googleapis.com`, `proactivebackend-pa.googleapis.com`, `pixelonboarding-pa.googleapis.com`, `remoteprovisioning.googleapis.com` — [Leith 2025](https://www.scss.tcd.ie/doug.leith/pubs/cookies_identifiers_and_other_data.pdf)

**What Google says Android needs (Android Enterprise network requirements)**
- Google Play and updates: `play.google.com`, `android.com`, `google-analytics.com`, `googleusercontent.com`, `*.gstatic.com`, `*.gvt1.com`, `*.gvt2.com`, `*.gvt3.com`, `*.ggpht.com`, `dl.google.com`, `dl-ssl.google.com`, `android.apis.google.com`, on TCP 443 and TCP/UDP 5228-5230. Google lists `google-analytics.com` under this purpose — [Google: Android Enterprise network requirements](https://support.google.com/work/android/answer/10513641?hl=en)
- FCM/GCM: `fcm.googleapis.com`, `fcm-xmpp.googleapis.com`, `gcm-http.googleapis.com`, `gcm-xmpp.googleapis.com`, `android.googleapis.com`, `firebaseinstallations.googleapis.com`. FCM through a firewall also needs `mtalk.google.com`, `mtalk4.google.com`, `alt1-mtalk.google.com` … `alt8-mtalk.google.com` and `device-provisioning.googleapis.com` on TCP 443 and 5228-5230 (XMPP also uses 5235/5236) — [Google](https://support.google.com/work/android/answer/10513641?hl=en)
- Authentication: `accounts.google.com` and `accounts.google.[country]`. EMM/Google APIs: `*.googleapis.com`, `m.google.com` — [Google](https://support.google.com/work/android/answer/10513641?hl=en)
- Connectivity check: `connectivitycheck.android.com`, `connectivitycheck.gstatic.com`, `www.google.com/generate_204`. OTA: `ota.googlezip.net`, `ota-cache1.googlezip.net`, `ota-cache3.googlezip.net`. NTP: `time.google.com`. Play Protect: `android-safebrowsing.google.com`, `safebrowsing.google.com`. CRL: `pki.google.com`, `clients1.google.com`. Backend (crash reporting, time sync and more): `clients2`–`clients6.google.com` — [Google](https://support.google.com/work/android/answer/10513641?hl=en)
- Logging and metrics: `firebaselogging.googleapis.com` is listed as "AMAPI SDK logging and metrics support" — [Google](https://support.google.com/work/android/answer/10513641?hl=en)

**Breakage reports from Pi-hole users**
- Blocking `play.googleapis.com` stops Play Store app downloads. Users report downloads stuck on "Pending…". They also report needing to allow `gvt1.com`, `gvt2.com`, `gvt3.com` and `android.clients.google.com` — [pi-hole/pi-hole #2503](https://github.com/pi-hole/pi-hole/issues/2503); [Pi-hole discourse: whitelist still being blocked](https://discourse.pi-hole.net/t/whitelist-still-being-blocked/8920); [pi-hole/pi-hole #1893](https://github.com/pi-hole/pi-hole/issues/1893); [Pi-hole discourse: Pi Hole and Play Store](https://discourse.pi-hole.net/t/pi-hole-and-play-store/48898)
- Perflyst's android-tracking list deliberately comments out `clients1.google.com` ("blocks chromecast") — [Perflyst android-tracking.txt](https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt)

**Where the ad/analytics hosts appear in curated lists (supports "safe to block")**
- The Exodus "Google AdMob" network signature covers `doubleclick.net`, `mobileads.google.com`, `ads.google.com`, `googlesyndication.com`, `googleadservices.com`, `googleads.g.doubleclick.net`, `adservice.google.*`, `adservice.g.cn`. "Google Firebase Analytics" covers `firebase.com` and `firebaselogging-pa.googleapis.com`. "Google CrashLytics" covers `crashlytics.com`. "Google Analytics" covers `google-analytics.com` — [Exodus trackers API](https://reports.exodus-privacy.eu.org/api/trackers)
- AdGuard Tracking Protection (filter 3, updated 2026-09-25) contains `||app-measurement.com^`, `||google-analytics.com^`, `||googleadservices.com^`, `||adservice.google.`, `||ssl-google-analytics.l.google.com^` and two `crashlyticsreports-pa.googleapis.com` rules. It only has `firebaselogging-pa.googleapis.com` scoped to one domain — [AdGuard filter 3](https://filters.adtidy.org/extension/ublock/filters/3.txt)
- GoodbyeAds contains `firebaselogging-pa.googleapis.com`, `firebaselogging.googleapis.com`, `firebase-settings.crashlytics.com` and `app-measurement.com` — [GoodbyeAds hosts](https://cdn.jsdelivr.net/gh/jerryn70/GoodbyeAds@master/Hosts/GoodbyeAds.txt)
- Perflyst lists `app-measurement.com`, `e.crashlytics.com`, `reports.crashlytics.com`, `settings.crashlytics.com`, `www.googleadservices.com`, `googleads.g.doubleclick.net`, `securepubads.g.doubleclick.net`, `ad.doubleclick.net`, `ssl.google-analytics.com`, `adservice.google.de`, `ade.googlesyndication.com`, `id.google.de` and `federatedml-pa.googleapis.com` — [Perflyst](https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt)
- None of the lists I checked (HaGeZi native.*, AdGuard 3/11, GoodbyeAds, Perflyst) block `play.googleapis.com` or `android.clients.google.com` (grep on 2026-09-25).

**Catalog: Google/GMS hostnames by DNS-block safety**

| Host | Seen/purpose | DNS-block status |
|---|---|---|
| `app-measurement.com`, `region1.app-measurement.com` | Firebase/Google Analytics; first startup call; Play Store events with ad ID ([Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf), [2025](https://www.scss.tcd.ie/doug.leith/pubs/cookies_identifiers_and_other_data.pdf)) | Safe. Listed by AdGuard, Perflyst and GoodbyeAds. `||app-measurement.com^` covers `region1` |
| `googleads.g.doubleclick.net`, `*.doubleclick.net` | DSID ad cookie set by GMS ([Leith 2025](https://www.scss.tcd.ie/doug.leith/pubs/cookies_identifiers_and_other_data.pdf)) | Safe for OS function. Already in the user's list via `||doubleclick.net^` |
| `www.googleadservices.com` | YouTube sends RDID ([Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)) | Safe for OS. Breaks click-through on Google Shopping/Search ad links **(inferred)** |
| `pagead2.googlesyndication.com`, `*.googlesyndication.com`, `adservice.google.*` | AdMob / ad serving ([Exodus](https://reports.exodus-privacy.eu.org/api/trackers)) | Safe. Removes in-app AdMob ads. Some "watch ad for reward" features stop working **(inferred)** |
| `ssl.google-analytics.com`, `google-analytics.com` | Clock app GA batch ([Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)) | Probably safe: widely blocked by AdGuard. Caveat: Google lists `google-analytics.com` under "Google Play and updates" ([Google](https://support.google.com/work/android/answer/10513641?hl=en)). I found no report of Play breaking, but watch for it |
| `firebaselogging-pa.googleapis.com`, `firebaselogging.googleapis.com` | Firebase/Clearcut-style logging; AMAPI SDK metrics ([Google](https://support.google.com/work/android/answer/10513641?hl=en), [Exodus](https://reports.exodus-privacy.eu.org/api/trackers)) | Safe on personal devices. On work-profile/EMM devices it only loses AMAPI metrics **(inferred)** |
| `crashlyticsreports-pa.googleapis.com`, `firebase-settings.crashlytics.com`, `settings.crashlytics.com`, `reports.crashlytics.com`, `e.crashlytics.com` | Crash reporting SDK ([AdGuard 3](https://filters.adtidy.org/extension/ublock/filters/3.txt), [GoodbyeAds](https://cdn.jsdelivr.net/gh/jerryn70/GoodbyeAds@master/Hosts/GoodbyeAds.txt), [Perflyst](https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt)) | Safe: apps lose only crash reports |
| `federatedml-pa.googleapis.com` | Federated learning ([Perflyst](https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt)) | Believed safe (Perflyst has blocked it since 2021) |
| `growth-pa.googleapis.com`, `mobilenetworkscoring-pa.googleapis.com` | Promos; Wi-Fi quality ([Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)) | Uncertain. No breakage data found. Try blocking and test |
| `youtubei.googleapis.com` | YouTube API and logevent ([Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)) | Do not block: it is the YouTube app's main API **(inferred from path usage)** |
| `play.googleapis.com` | Clearcut telemetry `/log/batch` and `/play/log`, but also Play Store traffic | **Breaks Play Store downloads** ([pi-hole #2503](https://github.com/pi-hole/pi-hole/issues/2503)) |
| `play.google.com` (incl. `/log`) | Play Store; telemetry logger ([Leith 2025](https://www.scss.tcd.ie/doug.leith/pubs/cookies_identifiers_and_other_data.pdf)) | **Breaks Play Store** (required per [Google](https://support.google.com/work/android/answer/10513641?hl=en)) |
| `android.clients.google.com` | Check-in (IMEI/serial/MAC/Android ID), Firebase | **Breaks** Play downloads/registration ([pi-hole #2503](https://github.com/pi-hole/pi-hole/issues/2503)) |
| `www.googleapis.com` | experimentsandconfigs telemetry and many APIs | **Breaks** Play/EMM/Google APIs ([Google](https://support.google.com/work/android/answer/10513641?hl=en)) |
| `android.googleapis.com`, `fcm.googleapis.com`, `mtalk.google.com`, `mtalk4.google.com`, `alt1…alt8-mtalk.google.com`, `firebaseinstallations.googleapis.com` | FCM push | **Do not block**: breaks push notifications ([Google](https://support.google.com/work/android/answer/10513641?hl=en)) |
| `accounts.google.com`, `android.apis.google.com` | Login/auth, Play | **Do not block**: breaks Google login ([Google](https://support.google.com/work/android/answer/10513641?hl=en)) |
| `connectivitycheck.gstatic.com`, `connectivitycheck.android.com`, `www.google.com` (generate_204) | Captive-portal/connectivity check | **Do not block**: Wi-Fi shows as "no internet" or the phone switches to mobile data **(inferred; Google lists as required)** |
| `*.gvt1.com`, `*.gvt2.com`, `*.gvt3.com`, `dl.google.com`, `ota*.googlezip.net`, `time.google.com`, `*safebrowsing.google.com`, `pki.google.com`, `clients1–6.google.com` | App/OTA downloads, NTP, Play Protect, CRL, backend | **Do not block** ([Google](https://support.google.com/work/android/answer/10513641?hl=en)) |

**Android Advertising ID**
- When a user deletes the advertising ID in Android Settings, apps that try to read it get "a string of zeros instead of the identifier". This rolled out on Android 12 from late 2021 and on all Google Play services devices from 1 April 2022 — [Play Console Help: Advertising ID](https://support.google.com/googleplay/android-developer/answer/6048248?hl=en)
- Path on current versions: Settings > Security & privacy > Privacy > Ads > Delete advertising ID (some builds: Settings > Google > All services > Ads) — [Privacy International guide](https://privacyinternational.org/guide-step/4317/android-opt-out-targeted-ads-and-renew-your-advertising-id); [NAI](https://thenai.org/how-to-opt-out/advertising-privacy-settings-on-mobile-devices/)

### Inferences
- DNS blocking reduces Google telemetry but cannot remove the largest flows (Clearcut via `play.googleapis.com`, experiments via `www.googleapis.com`, check-in via `android.clients.google.com`). They share hostnames with essential services, so the only fix is a de-Googled OS or not signing in / microG.
- Google lists `google-analytics.com` as needed for Play and updates. Blocking it is common and I found no breakage reports, but it is the first thing to allow if Play updates misbehave.
- Because the user's list uses `$important` on `doubleclick.net`, the DSID cookie connection is already blocked. The Leith 2025 paper gives no sign that GMS login depends on it.

### Gaps
- No primary source measures which Google hosts Android 15/16 (2025-2026 builds) contact. The newest measurement is Leith's Android 14 / GMS 24.47 study (Dec 2024 build).
- No authoritative breakage test for `growth-pa`, `mobilenetworkscoring-pa`, `firebaselogging-pa` or `google-analytics.com` on personal devices. Status is inferred from list inclusion.
- I did not find Google documentation for the "Usage & diagnostics" data endpoints. Leith quotes Google's UI text: turning it off "doesn't affect your device's ability to send the information needed for essential services".

---

## 2. Research papers measuring Android phone-home traffic (Leith/TCD and later)

### Takeaway
Leith's group has shown: (1) Pixel/Google Android sends telemetry every ~4.5 min even with diagnostics off (2021). (2) Samsung, Xiaomi, Huawei and Realme add OEM and third-party telemetry on top of Google's, with no opt-out, while LineageOS without GApps and /e/OS send nothing to their developers (2021). (3) GMS stores advertising and tracking cookies and identifiers without consent, even before any Google app is opened (Android 14, published 2025/26).

### Cited Findings
- "Mobile Handset Privacy: Measuring the Data iOS and Android Send to Apple and Google" (Leith, 2021): both OSes share the IMEI, hardware serial, SIM serial, IMSI and phone number with Apple/Google. Google collects far more than Apple. On a Pixel you can avoid some of this by starting up offline and disabling services — [PDF](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- "Android Mobile OS Snooping By Samsung, Xiaomi, Huawei and Realme Handsets" (Liu, Patras, Leith, 6 Oct 2021, EU models): "even when minimally configured and the handset is idle these vendor-customized Android variants transmit substantial amounts of information to the OS developer and also to third-parties (Google, Microsoft, LinkedIn, Facebook etc)… There is no opt out from this data collection." — [PDF](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)
- In the same paper, data volume to Google is at least 10× that to the OEM, rising to about 30× for Xiaomi, Huawei and Realme. Heytap (Realme's partner) uploads 3-4× more than Samsung, Xiaomi or Huawei. LineageOS sends similar volumes to Google (via GApps) but nothing to LineageOS. /e/OS (microG) sends nothing to Google or /e/ — [PDF](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)
- Hostnames named in the 2021 OEM paper:
  - Samsung: `api.omc.samsungdm.com` (logs SIM insertion), `samsung-directory.edge.hiyaapi.com` (logs making and receiving calls), `capi.samsungcloud.com` (US)
  - Xiaomi: `tracking.intl.miui.com`, `api.ad.intl.xiaomi.com`, `data.mistat.intl.xiaomi.com` (servers estimated in Singapore; AES-encrypted payloads from Settings and Security Center)
  - Realme/Heytap: `dceuex.push.heytapmobile.com` (com.heytap.mcs events, AES/CBC with hard-coded key), `shorteuex.push.heytapmobile.com` (registration ID)
  - Huawei: `query.hicloud.com`, `pebed.dmevent.net` (HiMovie events), `apkrep.ff.avast.com` (every installed app sent to Avast scanning), `mclean.cloud.360safe.com`, `mvconf.cloud.360safe.com` (Qihoo 360)
  - Microsoft preinstalls: `mobile.pipe.aria.microsoft.com`, `telemetry.api.swiftkey.com`, `app.adjust.com`, `www.linkedin.com`
  - Operator app (SFR): `sun-apps.sfr.com`
  - Source for all of the above: [PDF](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)
- Google Android advertising ID sharing: Samsung sends the Google Ad ID to Microsoft servers, Xiaomi sends it to Xiaomi, and Realme sends it to Heytap. This allows cross-linking — [PDF](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)
- "Cookies, Identifiers and Other Data That Google Silently Stores on Android Handsets" (Leith; preprint 2025, journal version in Computers & Security 2026, article S016740482600026X) covers the DSID cookie, Google Android ID and Firebase tokens (details in section 1) — [PDF](https://www.scss.tcd.ie/doug.leith/pubs/cookies_identifiers_and_other_data.pdf); [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S016740482600026X); [TCD E3 news](https://www.tcd.ie/e3/news/google-apps-silently-store-cookies-and-identifiers-on-android-phones-study-finds/)

### Inferences
- The OEM hostnames are from 2021 EU firmware. Current One UI 8 / HyperOS 2-3 / ColorOS 15-16 builds very likely use changed or extra hosts, which is why maintained lists like HaGeZi native.* matter more than paper hostnames.

### Gaps
- I found no peer-reviewed 2025-2026 measurement of One UI, HyperOS or ColorOS traffic comparable to the 2021 study. The other Leith Android-app papers (Google Dialer/Messages 2022, etc.) were not re-checked in this pass.
- No academic measurement of Motorola or current Pixel (Android 15/16) OEM-specific telemetry hostnames was found.

---

## 3. OEM telemetry domains (Samsung, Xiaomi/HyperOS, OPPO/Realme/OnePlus/ColorOS, Huawei/Honor, Vivo, Motorola, Pixel)

### Takeaway
HaGeZi's native.* lists are the best maintained and most complete source (all updated in September 2026). Below are the hosts relevant to phones, taken from those lists, AdGuard, GoodbyeAds and the Leith paper. They are candidates to add to the user's list. Main breakage risk: **Xiaomi's list includes `xmpush` (Mi Push) hosts**. Blocking them can break push notifications in apps that use Mi Push, typically China-market apps. HMS push hosts under `hicloud.com` may matter on Huawei phones in the same way **(inferred)**.

### Cited Findings

**Samsung** (HaGeZi native.samsung, 200 entries, last modified 23 Sep 2026)
- Device telemetry/diagnostics: `dc.dqa.samsung.com`, `dls-ddc.dqa.samsung.com`, `dls-udc.dqa.samsung.com`, `dc.di.atlas.samsung.com`, `ddf.di.atlas.samsung.com`, `dls-account.di.atlas.samsung.com`, `dqa-auth.di.atlas.samsung.com`, `regi.di.atlas.samsung.com`, `dc.di.runestone.samsung.com`, `dls.di.runestone.samsung.com`, `orsdls.di.runestone.samsung.com`, `orsfs.di.runestone.samsung.com`, `api.runestone.samsung.com`, `diagmon-policy.samsungdm.com`, `diagmon-serviceapi.samsungdm.com`, `report.gras.samsungdm.com`, `us-report.gras.samsungdm.com`, `analytics.bigdata.samsung.com`, `bigdata.ssp.samsung.com`, `metric.account-samsung.com`, `nmetrics.samsung.com`, `smetrics.samsung.com`, `event-tracking.samsung.com`, `analytics.mpay.samsung.com`, `ureca.samsungapps.com`, `sia.internet.apps.samsung.com`, `devicelog.samsungcloudsolution.net`, `osb.samsungqbe.com`, `osb-krsvc.samsungqbe.com`, `sspapi-prd.samsungrs.com` — [HaGeZi native.samsung](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt)
- Ads: `samsungads.com`, `samsungads.adsmeasurement.com` (HaGeZi). GoodbyeAds Samsung adds `ad.samsungads.com`, `ads.samsungads.com`, `config.samsungads.com`, `events.samsungads.com`, `samsungadhub.com`, `rd.samsungadhub.com`, `analytics.samsungknox.com`, `insights.samsung.com`, `gpm.samsungqbe.com`, `osb-ussvc.samsungqbe.com` — [GoodbyeAds-Samsung](https://cdn.jsdelivr.net/gh/jerryn70/GoodbyeAds@master/Extension/GoodbyeAds-Samsung-AdBlock.txt)
- AdGuard Tracking Protection also blocks `dc.dqa.samsung.com` — [AdGuard 3](https://filters.adtidy.org/extension/ublock/filters/3.txt)
- From Leith 2021: `api.omc.samsungdm.com` (SIM-insert logging), `samsung-directory.edge.hiyaapi.com` (call logging via Hiya caller ID). Blocking Hiya would probably break Samsung's caller-ID/spam feature **(inferred)** — [Leith OEM paper](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)
- HaGeZi's Samsung list also includes many TV ACR hosts (`acr-*-prd.samsungcloud.tv`, `log-*.samsungacr.com` in GoodbyeAds). These are TV-related, not phone, but harmless to include.

**Xiaomi / MIUI / HyperOS** (HaGeZi native.xiaomi, 345 entries, 11 Sep 2026)
- Analytics/tracking: `data.mistat.xiaomi.com`, `mistat.xiaomi.com`, `mistat.intl.xiaomi.com`, `mistat.india.xiaomi.com`, `mistat.rus.xiaomi.com`, `tracking.miui.com`, `tracking.intl.miui.com`, `tracking.eu.miui.com`, `api.collect.data.intl.miui.com`, `data.sec.miui.com`, `data.sec.intl.miui.com`, `stat.miui.com`, `stat.xiaomi.com`, `stat.www.xiaomi.com`, `mqs-log.miui.com`, `feedback.miui.com`, `migcreport.g.mi.com`, `tracker.ai.xiaomi.com`, `logs.n.xiaomi.com`, `report.n.xiaomi.com`, `log.pt.xiaomi.com`, `bugreport.pt.xiaomi.com`, `bugreport.xiaomi.net`, `in-miuilog.sms.intl.xiaomi.com`, `secure.report.iss.xiaomi.com`, `mlog.search.xiaomi.net`, `analytics.ff.avast.sec.miui.com`, `logupdate.avlyun.sec.miui.com`, `gstat.pandora.xiaomi.com`, `stat.pandora.xiaomi.com` — [HaGeZi native.xiaomi](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.xiaomi.txt)
- Ads: `ad.xiaomi.com`, `ad.mi.com`, `ad.miui.com`, `ad.intl.xiaomi.com`, `ad.eu.xiaomi.com`, `ad.india.xiaomi.com`, `ad.rus.xiaomi.com`, `api.ads.xiaomi.com`, `ad.cdn.pandora.xiaomi.com` (HaGeZi); `sdkconfig.ad.xiaomi.com`, `sdkconfig.ad.intl.xiaomi.com`, `abtest.mistat.xiaomi.com`, `storeconfig.mistat.intl.xiaomi.com` — [AdGuard 3](https://filters.adtidy.org/extension/ublock/filters/3.txt) (the sdkconfig hosts are also in GoodbyeAds)
- **Push, blocking can break notifications:** `api.xmpush.xiaomi.com`, `register.xmpush.global.xiaomi.com`, `api.xmpush.global.xiaomi.com`, `resolver.msg.global.xiaomi.net` and regional variants are in HaGeZi's Xiaomi list — [HaGeZi native.xiaomi](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.xiaomi.txt)
- `sa.api.intl.miui.com` (already in the user's list) was not re-verified against a 2026 source.

**OPPO / Realme / OnePlus / ColorOS / Heytap** (HaGeZi native.oppo-realme, 486 entries, 17 Sep 2026)
- Telemetry/logging: `log-eap.coloros.com`, `log-eap-in.coloros.com`, `log-eap-sg.coloros.com`, `dragate.dc.oppomobile.com`, `dragate-sg.dc.oppomobile.com`, `dragate-br.dc.oppomobile.com`, `dragate-{cn,in,sg}.dc.heytapmobi.com`, `obus-cn.dc.heytapmobi.com`, `dc.heytapmobile.com`, `dc-stat-in.heytapmobile.com`, `stat.browser.heytapmobi.com`, `logforward.browser.heytapmobi.com`, `report-{eu,in,sg}.uc.heytapmobile.com`, `dcintl.push.heytapmobi.com`, `device-ups.push.heytapmobi.com`, `userprofile.push.heytapmobi.com`, `id.push.heytapmobi.com` — [HaGeZi native.oppo-realme](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.oppo-realme.txt)
- Ads: `ads.heytapmobi.com`, `ads.heytapmobile.com`, `adx-ads-{fr,ru}.heytapmobile.com`, `cldata-ads-{fr,ru}.heytapmobile.com`, `ads.oppomobile.com`, `adsfs.oppomobile.com`, `adsfs-sdkconfig.heytapimage.com` — [HaGeZi](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.oppo-realme.txt)
- HaGeZi also lists `push.heytapmobile.com` and `push-dc-us.heytapmobile.com`. Blocking these could affect ColorOS/OPPO push **(inferred)**. Leith saw `dceuex.push.heytapmobile.com` and `shorteuex.push.heytapmobile.com` carrying telemetry and registration IDs — [Leith OEM paper](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)
- OnePlus: HaGeZi's OPPO/Realme list has 0 OnePlus-branded entries (grep, 2026-09-25). AdGuard blocks `click.oneplus.com`, `click.oneplus.cn`, `open.oneplus.net`, `apaff.oneplus.com` — [AdGuard 3](https://filters.adtidy.org/extension/ublock/filters/3.txt). GoodbyeAds adds `oplus.umeng.com`, `oplus.cnzz.com`, `apioplus.cnzz.com`, `moa-upload-online.coloros.com` — [GoodbyeAds](https://cdn.jsdelivr.net/gh/jerryn70/GoodbyeAds@master/Hosts/GoodbyeAds.txt). Current OnePlus phones run ColorOS/OxygenOS on the Heytap/ColorOS back-end, so the OPPO list also applies to them **(inferred)**.

**Huawei / Honor** (HaGeZi native.huawei, 135 entries, 11 Sep 2026)
- `data.hicloud.com`, `logservice.hicloud.com`, `logservice1.hicloud.com`, `logbak.hicloud.com`, `logservice-dra.platform.hicloud.com`, `logservice-dre.platform.hicloud.com`, `metrics*.dt.dbankcloud.cn/.com`, `datacollector-dra.dt.dbankcloud.cn`, `datacollector-dre.dt.dbankcloud.cn`, `ubacollect-drcn.cloud.dbankcloud.cn`, `logservice1.dbankcloud.com`, `nebula-collector.huawei.com`, `ads.cloud.huawei.com`. Honor: `log-{dra,drcn,dre,drru}.platform.hihonorcloud.com`, `ads-*.platform.hihonorcloud.com`, `tracking-data.platform.hihonorcloud.com` — [HaGeZi native.huawei](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.huawei.txt)
- Perflyst lists `servicesupport.hicloud.com` — [Perflyst](https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt). Leith: `query.hicloud.com`, `pebed.dmevent.net`, Avast `apkrep.ff.avast.com`, Qihoo `*.cloud.360safe.com` — [Leith](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)
- Caution: Exodus's HMS Core signature covers all of `hicloud.com` and `dbankcloud.*` ([Exodus API](https://reports.exodus-privacy.eu.org/api/trackers)). Wildcard-blocking those domains would break AppGallery, HMS push and Huawei ID **(inferred)**. Use HaGeZi's specific subdomains instead.

**Vivo** (HaGeZi native.vivo, 234 entries, 18 Sep 2026)
- `adlog.vivo.com.cn`, `adsdk.vivo.com.cn`, `adxlog-adnet.vivo.com.cn`, `dsplog-adnet.vivo.com.cn`, `tracking-adnet.vivo.com.cn`, `adlog.vivo.com`, `ads-api.vivo.com`, `asia-adlog.vivoglobal.com`, `in-adlog.vivoglobal.com`, `asia-abeacdataonrt-stsdk.vivoglobal.com`, `kz-cname-sin01-bigdata.vivoglobal.com`, `tr-gdpr-vgc-datacenter.vivoglobal.com`, plus `*-vpushonrt-stsdk.vivoglobal.com` (push statistics SDK; possibly push-related) — [HaGeZi native.vivo](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.vivo.txt)

**Motorola / Pixel**
- AdGuard blocks only Motorola marketing hosts (`tracking.motorolasolutions.com`, `etscampaign.motorola.com`, `campaign.motorolasolutions.com` and similar), which are web marketing and not device telemetry — [AdGuard 3](https://filters.adtidy.org/extension/ublock/filters/3.txt)
- For Pixel, telemetry goes to the Google endpoints in section 1. Leith 2025 saw `pixelonboarding-pa.googleapis.com` — [Leith 2025](https://www.scss.tcd.ie/doug.leith/pubs/cookies_identifiers_and_other_data.pdf)

**Third-party preloads (any OEM)**
- `mobile.pipe.aria.microsoft.com` (Microsoft/SwiftKey/Office preloads), `telemetry.api.swiftkey.com`, `app.adjust.com` — [Leith OEM paper](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf). `mobile.pipe.aria.microsoft.com` is also Microsoft 365 telemetry, relevant to the parallel Microsoft research.

### Inferences
- For the user's `$important` list, the lowest-risk additions are the explicit telemetry and ads subdomains above. Leave out push (`xmpush`, `*.push.heytapmobile.com`, Vivo `vpush*`) and whole-domain wildcards (`hicloud.com`, `dbankcloud.*`, `samsungdm.com`). `samsungdm.com` also carries Samsung firmware (FOTA) and device management traffic **(inferred; not verified)**.
- Subscribing to HaGeZi native lists directly in Pi-hole (domains format) is easier to maintain than copying entries.

### Gaps
- No verified 2026 source for Samsung Push Service (SPP) hostnames, Motorola device telemetry hosts (e.g. Moto "Improve your device" data), or Pixel-specific OEM hosts. I did not include any.
- `sdkconfig.ad.xiaomi.com` comes from AdGuard and GoodbyeAds, not HaGeZi. I did not confirm whether it still resolves in 2026.

---

## 4. Existing blocklists: raw URLs and maintenance status (checked 2026-09-25)

### Takeaway
HaGeZi native.* lists and the AdGuard filters are actively maintained (updated within days or hours). 1Hosts Lite is maintained at its GitHub Pages URL. **GoodbyeAds (last update Nov 2024) and Perflyst android-tracking (last commit Nov 2021) are stale.** Exodus is a tracker-signature database with an API, not a DNS list.

### Cited Findings
| List | Raw URL (Pi-hole-compatible) | Status on 2026-09-25 |
|---|---|---|
| HaGeZi native.samsung | `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.samsung.txt` (also `/domains/…` and `/wildcard/…-onlydomains.txt`) | 200 entries, modified 23 Sep 2026, "Expires: 8 hours" — [file](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/native.samsung.txt) |
| HaGeZi native.xiaomi | `…/adblock/native.xiaomi.txt` | 345 entries, 11 Sep 2026 — [file](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/native.xiaomi.txt) |
| HaGeZi native.oppo-realme | `…/adblock/native.oppo-realme.txt` | 486 entries, 17 Sep 2026 — [file](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/native.oppo-realme.txt) |
| HaGeZi native.vivo | `…/adblock/native.vivo.txt` | 234 entries, 18 Sep 2026 — [file](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/native.vivo.txt) |
| HaGeZi native.huawei | `…/adblock/native.huawei.txt` | 135 entries, 11 Sep 2026 — [file](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/native.huawei.txt) |
| HaGeZi native.tiktok | `…/adblock/native.tiktok.txt` | 436 entries, 18 Sep 2026 — [file](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/native.tiktok.txt) |
| HaGeZi other native lists | `native.apple`, `native.amazon`, `native.winoffice`, `native.lgwebos`, `native.roku` exist (README) | [HaGeZi README](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/README.md) |
| HaGeZi Encrypted DNS Bypass | `…/adblock/doh.txt` | 3,334 entries, 25 Sep 2026 — [file](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/doh.txt) |
| HaGeZi DoH/VPN/Tor/Proxy Bypass | `…/adblock/doh-vpn-proxy-bypass.txt` | 16,313 entries, 25 Sep 2026 — [file](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/doh-vpn-proxy-bypass.txt) |
| Perflyst android-tracking | `https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/android-tracking.txt` | 80-ish domains. Last commit 24 Nov 2021 ("Add federatedml-pa.googleapis.com"): **stale but still valid core** — [commits](https://github.com/Perflyst/PiHoleBlocklist/commits/master/android-tracking.txt) |
| AdGuard Mobile Ads (filter 11) | `https://filters.adtidy.org/extension/ublock/filters/11.txt` | TimeUpdated 2026-09-25, v2.0.72.33 — [file](https://filters.adtidy.org/extension/ublock/filters/11.txt) |
| AdGuard Tracking Protection (filter 3, includes mobile trackers) | `https://filters.adtidy.org/extension/ublock/filters/3.txt` | TimeUpdated 2026-09-25, ~330k lines — [file](https://filters.adtidy.org/extension/ublock/filters/3.txt). Note: this is a browser-syntax list. Pi-hole only uses the plain `||domain^` rules |
| GoodbyeAds (jerryn70) | `https://raw.githubusercontent.com/jerryn70/GoodbyeAds/master/Hosts/GoodbyeAds.txt`; extensions `…/Extension/GoodbyeAds-Samsung-AdBlock.txt`, `…/GoodbyeAds-Xiaomi-Extension.txt` | Main list 277,831 entries, "Updated: Nov 21 2024". Samsung and Xiaomi extensions updated 19 Nov 2024: **not updated in ~22 months** — [file](https://cdn.jsdelivr.net/gh/jerryn70/GoodbyeAds@master/Hosts/GoodbyeAds.txt) |
| 1Hosts Lite | `https://badmojr.github.io/1Hosts/Lite/adblock.txt` | Last modified 2026-09-03 — [file](https://badmojr.github.io/1Hosts/Lite/adblock.txt). The old mirror `o0.pages.dev/Lite/adblock.txt` was last modified 2025-12-25 and is much smaller: **use the github.io URL** — [mirror](https://o0.pages.dev/Lite/adblock.txt) |
| Exodus Privacy trackers | API `https://reports.exodus-privacy.eu.org/api/trackers` (JSON with `network_signature` regexes) | 432 trackers; site version εxodus v1.33.0 — [trackers page](https://reports.exodus-privacy.eu.org/en/trackers/), [API](https://reports.exodus-privacy.eu.org/api/trackers) |

### Inferences
- For a Pi-hole user who already maintains an ABP-syntax list, the most useful additions are the HaGeZi native.samsung, native.xiaomi, native.oppo-realme, native.huawei and native.vivo lists (only for brands actually in the house), plus HaGeZi `doh.txt` to stop encrypted-DNS bypass.
- Exodus signatures are domain regexes, not hostnames. They are good for auditing an app (TrackerControl uses the same kind of signatures) but not for direct import.

### Gaps
- GitHub API access was blocked in this environment, so I could not read HaGeZi's issue tracker for known native-list false positives (e.g. Xiaomi push).
- I did not check whether AdGuard's separate "Mobile Tracking" category exists as its own list in 2026. In the current registry, mobile tracking domains appear to be inside filter 3.

---

## 5. DNS bypass on Android and how to force Pi-hole

### Takeaway
Android's Private DNS (DoT on port 853, Android 9+) takes priority over the DHCP-provided Pi-hole when set to a hostname (strict mode). In "Automatic" mode Android upgrades to DoT only if the network's own DNS server supports it, and Pi-hole does not, so Automatic falls back to plain DNS to Pi-hole. Chrome's Secure DNS "automatic" mode only upgrades to the same provider's DoH. The practical fixes: set Private DNS to Off or Automatic; on the router, block outbound TCP/UDP 853 and redirect or block port 53 to anything other than Pi-hole; add HaGeZi `doh.txt` to Pi-hole; when away from home, use Pi-hole over WireGuard or Tailscale.

### Cited Findings
- Android 9: "By default, devices automatically upgrade to DNS over TLS if a network's DNS server supports it." Users can set a Private DNS mode under Network & internet settings — [Android Developers Blog, DNS over TLS support in Android P](https://android-developers.googleblog.com/2018/04/dns-over-tls-support-in-android-p.html)
- DoT supports strict and opportunistic profiles: strict requires an authenticated connection to the named server, and opportunistic falls back to unencrypted DNS if TLS fails — [Wikipedia: DNS over TLS](https://en.wikipedia.org/wiki/DNS_over_TLS)
- Pi-hole users report that with Private DNS set to a provider (e.g. dns.google), Android bypasses Pi-hole entirely, and that "No internet" occurs when Private DNS points at an unreachable or non-DoT resolver — [Pi-hole discourse: No internet with Private DNS](https://discourse.pi-hole.net/t/no-internet-with-pi-hole-when-using-androids-private-dns-feature/71818); [Pi-hole discourse: opportunistic DoT](https://discourse.pi-hole.net/t/home-network-dns-opportunitstic-dot-for-android-and-linux/50736)
- You can put a TLS front-end (e.g. stunnel/nginx on 853) in front of Pi-hole so that strict-mode Private DNS still goes through Pi-hole, even off-network if exposed. This is a community how-to — [svarun.dev guide](https://blog.svarun.dev/configure-pi-hole-with-dns-over-tls-private-dns); [Pi-hole discourse: Private DNS hostname](https://discourse.pi-hole.net/t/private-dns-hostname/18734)
- Chrome Secure DNS automatic mode uses "auto-upgrading to the current DNS provider's DoH server which offers the same features". Managed deployments are opted out automatically. "Split Horizon setups should continue to work as is." — [Chromium: DNS over HTTPS](https://www.chromium.org/developers/dns-over-https/)
- HaGeZi's Encrypted DNS Bypass list (`doh.txt`, 3,334 entries) blocks DoH/DoT resolver hostnames including `dns.google`, `cloudflare-dns.com`, `one.one.one.one`, `dns.quad9.net`, `doh.opendns.com`, `dns.nextdns.io`. The larger variant also blocks VPN, Tor and proxies — [HaGeZi doh.txt](https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/doh.txt)

### Inferences
- With Pi-hole as DHCP DNS and Private DNS on "Automatic", the phone uses Pi-hole: Pi-hole does not answer on 853, so opportunistic mode falls back. The risk is a user or OEM setting Private DNS to a hostname, which strict mode then enforces. Blocking that hostname's resolution (HaGeZi `doh.txt`) makes strict mode fail with "Private DNS server cannot be accessed" rather than silently bypassing. Blocking TCP 853 at the router gives the same result for resolvers hard-coded by IP.
- Chrome's auto-upgrade does not apply to a Pi-hole resolver, because Pi-hole is not a known DoH provider. A manually chosen Chrome "custom" provider would bypass Pi-hole, and HaGeZi `doh.txt` plus blocking known DoH IPs on 443 would stop that.
- Apps with hard-coded DNS servers (plain port 53 to 8.8.8.8, for example) can be caught with a router NAT redirect of all outbound UDP/TCP 53 to Pi-hole. Apps that use hard-coded DoH over 443 can only be stopped with IP-based blocklists, not by Pi-hole alone.
- Off-network: a WireGuard or Tailscale tunnel with Pi-hole as the tunnel DNS server (Tailscale "override local DNS") keeps filtering on mobile data. Private DNS must stay Off/Automatic, because a strict-mode hostname takes precedence over VPN-provided DNS **(inferred; not verified in an official doc)**.

### Gaps
- I could not reach an official AOSP page that explains the Android 13+ DoH-in-Private-DNS behaviour (which providers are auto-detected) and how Private DNS interacts with VPN DNS. The source.android.com DNS resolver page does not cover it.
- No source was found documenting specific Android system components that hard-code DNS IPs in 2026.

---

## 6. On-device mitigations

### Takeaway
The settings changes that help: delete the advertising ID, turn off Usage & diagnostics, Web & App Activity and Location History/Timeline, and turn off OEM "Customization Service" and diagnostic data toggles (Samsung) or "User Experience Programme" toggles (Realme/Xiaomi). They reduce but do not stop telemetry: Leith shows data still flows with them off. Stronger options: ADB debloating with UAD-ng (v1.2.0), per-app firewalls (NetGuard, RethinkDNS, TrackerControl), or a de-Googled OS (GrapheneOS, CalyxOS, LineageOS without GApps, /e/OS with microG). In the 2021 study, /e/OS and LineageOS were the only variants that sent nothing to their developers.

### Cited Findings
- Delete advertising ID: apps then read zeros (Android 12+, all GMS devices since April 2022) — [Play Console Help](https://support.google.com/googleplay/android-developer/answer/6048248?hl=en)
- Turning off Google's Usage & Diagnostics does not stop the Clearcut, experiments and check-in flows. Google's own UI says turning it off "doesn't affect your device's ability to send the information needed for essential services such as system updates and security" — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- On a Pixel, starting up with the network disconnected and then disabling services limits data sharing, though some remains — [Leith 2021](https://www.scss.tcd.ie/doug.leith/apple_google.pdf)
- In the OEM study the testers unchecked Samsung's "Send Diagnostic Data Automatically", "Personalised Ads" and "User Experience Programme", and Realme's "User Experience Programme" and "Uploading Device Error" toggles. Data collection continued: "no opt out" — [Leith OEM paper](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)
- Samsung Customization Service turns on when a Samsung account is created and builds a profile for ads and recommendations. Turn it off under Samsung account settings. Send diagnostic data lives at Settings > Security and privacy > More privacy settings. One UI updates reportedly re-enable settings, so re-check after updates — [MakeUseOf](https://www.makeuseof.com/turn-off-samsung-customization-service-for-privacy/); [How-To Geek](https://www.howtogeek.com/stop-samsung-and-google-from-collecting-your-phone-data-disable-these-settings/); [Samsung US support](https://www.samsung.com/us/support/answer/ANS10002544/)
- UAD-ng (Universal Android Debloater Next Generation) is a Rust GUI that uses ADB to debloat non-rooted phones. It labels packages as Recommended, Advanced, Expert or Unsafe and covers Samsung, Xiaomi, OnePlus and Pixel. Latest version tag seen: 1.2.0 — [GitHub repo](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/); [jsDelivr tags](https://data.jsdelivr.com/v1/packages/gh/Universal-Debloater-Alliance/universal-android-debloater-next-generation). For Xiaomi, `com.miui.msa.global` (MSA) is described as telemetry/ad injection — [Droid Rooter 2026 guide](https://www.droidrooter.com/blog/android-debloating-guide-2026) (secondary source)
- LineageOS without GApps collects nothing beyond what GApps sends to Google. /e/OS with microG sent no data to Google or /e/ — [Leith OEM paper](https://www.scss.tcd.ie/doug.leith/Android_privacy_report.pdf)

### Inferences
- Local VPN firewalls (NetGuard, RethinkDNS, TrackerControl) use Android's single VPN slot, so they conflict with a WireGuard/Tailscale tunnel back to Pi-hole. RethinkDNS can act as a WireGuard client and firewall at the same time **(inferred from product design; not verified in this pass)**.
- GrapheneOS and CalyxOS were not in Leith's measurements. Their privacy claims rest on their own documentation, which was not fetched here.

### Gaps
- I did not fetch primary docs for NetGuard, RethinkDNS, TrackerControl, GrapheneOS or CalyxOS in this pass, because of the tool-call budget. Their capabilities are stated only as inferences.
- The Web & App Activity and Location History (now "Timeline", stored on-device) steps were not re-verified against a 2026 Google help page.
