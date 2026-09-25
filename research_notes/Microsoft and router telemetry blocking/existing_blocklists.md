# Existing blocklists for Microsoft telemetry, tracking and phone-home traffic

Method note: every raw URL below was fetched on 2026-09-25 from this session with `curl`. The status code, line or entry count and header dates were recorded from those fetches. Repo commit dates come from shallow `git clone` metadata, because the GitHub REST API was not reachable from this session. Coverage comparisons use a 62-domain test set: 31 telemetry or ad endpoints and 31 functional endpoints (Windows Update, Store, activation, sign-in, Xbox, Teams, Outlook, OneDrive, NCSI, CRL, time). The set was checked against each list with a small script. Adblock-style `||x^` and wildcard lists were matched with subdomain semantics. Hosts lists were matched exactly, which is how Pi-hole treats them. The script ignored `@@` exceptions, and that matters for the "Microsoft-Blocker" rows, which are flagged below.

## Q1. WindowsSpyBlocker (crazy-max): lists, raw URLs, freshness, maintenance

### Takeaway
WindowsSpyBlocker's app code still gets dependency bumps, the latest on 2026-08-30. Its blocklist data has not changed since 2022-05-16, so in practice the lists are unmaintained. Its `spy.txt` is still a Firebog "tick" list and is still used as a source by aggregators such as Energized. However, it misses the main modern Windows telemetry endpoints (`v10/v20/self.events.data.microsoft.com`), and it hard-blocks about 115 WNS push-notification nodes and about 100 Limelight CDN nodes. HaGeZi submitted `native.winoffice` to the AdGuard Home catalog as its explicit successor. Neither project publishes an ABP-syntax version of the WindowsSpyBlocker lists.

### Cited Findings
- **Lists (3 categories × many formats).** The repository `data/` tree has `hosts/{spy,extra,update}.txt` plus `_v6` variants, `dnscrypt/`, `eset/`, `firewall/` (IPs), `kaspersky/`, `openwrt/{spy,extra,update}/dnsmasq.conf` and `firewall.user`, `p2p/`, `proxifier/{..}/domains.txt|ips.txt`, and `simplewall/`. There is **no ABP/adblock format** and no top-level `dnsmasq/` directory (`data/dnsmasq/spy.txt` returns 404). — [WindowsSpyBlocker repo data tree](https://github.com/crazy-max/WindowsSpyBlocker/tree/master/data)
- **Raw URLs (verified 200):**
  - Spy: `https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt` (347 `0.0.0.0` entries)
  - Extra: `https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/extra.txt` (400 entries)
  - Update: `https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/update.txt` (539 entries)
  - OpenWrt dnsmasq: `https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/openwrt/spy/dnsmasq.conf` (also `extra/`, `update/`)
  - Firewall IPs: `https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/firewall/spy.txt`
  — [spy.txt](https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt), [extra.txt](https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/extra.txt), [update.txt](https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/update.txt)
- **Category semantics (from the project docs):**
  - Spy blocks Windows telemetry and is marked "Recommended".
  - Update "block[s] Windows Update".
  - Extra blocks "third party applications like Skype, Bing, Live, Outlook, NCSI, Microsoft Office", with the warning "ONLY use if you know what you do … these rules can also block Windows Update and other services … no support will be provided".

  The docs say rules come from traffic captured on Windows 10/11 Pro VMs, with dumps "cleaned monthly". — [docs/blocking-rules (in repo)](https://github.com/crazy-max/WindowsSpyBlocker/tree/master/docs)
- **Last data update.** The spy.txt header reads `Updated: 2022-05-16T13:25:00Z`. The last commit touching `data/` is from 2022-05-16 ("Update hosts for extra, spy and update rules"). The last tagged release is 4.39.0, also from 2022-05-16. — [spy.txt header](https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt); [repo commits](https://github.com/crazy-max/WindowsSpyBlocker/commits/master)
- **Repo activity.** The repository is not archived. Its latest commits are Dependabot Go-module bumps merged on 2026-08-30, plus "switch DNS resolutions to VirusTotal" on 2026-08-21. The domain data has not been refreshed. — [repo commits](https://github.com/crazy-max/WindowsSpyBlocker/commits/master)
- **License.** MIT ("Copyright (c) 2016-2022 CrazyMax"). — [LICENSE](https://github.com/crazy-max/WindowsSpyBlocker/blob/master/LICENSE)
- **Staleness has been reported.** Issue #510 was opened on 2023-10-08 asking for an update, citing new telemetry hosts such as `turing-writingassistance.edge.microsoft.com`. It is closed, and no maintainer reply is visible. — [Issue #510](https://github.com/crazy-max/WindowsSpyBlocker/issues/510)
- **Known breakage.** Issue #450 (2022-04-08): `i-db3p-cor004.api.p001.1drv.com` in spy.txt broke OneDrive sign-in under Pi-hole. The current spy.txt contains no `1drv.com` entries, which suggests the entry was removed in the May 2022 refresh. — [Issue #450](https://github.com/crazy-max/WindowsSpyBlocker/issues/450); verified by grep of the current spy.txt
- **Coverage gaps and risks (my test set).**
  - spy.txt does **not** block `v10.events.data.microsoft.com`, `v20.…`, `self.events.data.microsoft.com`, `settings-win.data.microsoft.com`, `activity.windows.com`, `arc.msn.com` or `fp.msedge.net`. Those are only in extra.txt.
  - spy.txt contains 115 `*.wns.windows.com` hosts (Windows Push Notification Service nodes), 100 `*.llnw.net` hosts (Limelight CDN), 9 `blob.core.windows.net` hosts, and `ztd.dds.microsoft.com` (Autopilot zero-touch).
  - extra.txt blocks `login.live.com`, `login.microsoftonline.com`, `outlook.office365.com`, `onedrive.live.com`, the `msftconnecttest.com`/`msftncsi.com` NCSI probes, `crl.microsoft.com`, `time.windows.com`, `licensing.mp.microsoft.com`, `activation-v2.sls.microsoft.com` and `storeedgefd.dsx.mp.microsoft.com`. It therefore breaks sign-in, Outlook, OneDrive, NCSI, activation and the Store.
  - update.txt blocks `windowsupdate.com`, `fe3.delivery.mp…`, `displaycatalog.mp…` and `ctldl.windowsupdate.com` (certificate trust list updates).

  — computed from the raw files above
- **Only 61 of the 347 spy.txt hosts are covered by HaGeZi native.winoffice.** Most of the difference is per-node WNS/Limelight/akadns hosts that HaGeZi deliberately does not carry. — computed from the raw files above
- **Still recommended by Firebog.** "Crazy Max's Microsoft Telemetry" (spy.txt) sits in Firebog's "Tracking & Telemetry Lists" with a green tick ("least likely to interfere with browsing"). — [firebog.net](https://firebog.net/)
- **Removed from the AdGuard Home catalog.** HaGeZi's July 2024 request to add the Windows/Office tracker list to AdGuard's HostlistsRegistry "explicitly positions this as a successor to the discontinued 'WindowsSpyBlocker - Hosts spy rules' list". The current registry `filters.json` contains `hagezi_windows_office_tracker_blocklist` (id 63) and no WindowsSpyBlocker entry. The old asset `filter_23.txt` is still served, with header "Last modified: 2024-10-30". — [HostlistsRegistry issue #507](https://github.com/AdguardTeam/HostlistsRegistry/issues/507); [filters.json](https://adguardteam.github.io/HostlistsRegistry/assets/filters.json); [filter_23.txt](https://adguardteam.github.io/HostlistsRegistry/assets/filter_23.txt)
- **Community view (Nov 2025).** A Privacy Guides thread asked whether WindowsSpyBlocker is "still good". One poster noted "nothing has been updated in 3 years" and another noted that its IP rules may go stale. Suggested alternatives included HaGeZi `native.winoffice` or HaGeZi Ultimate. — [Privacy Guides forum](https://discuss.privacyguides.net/t/windows-spyblocker-still-good-in-2025/32656)

### Inferences
- For a 2026 Pi-hole or ABP user, WSB spy.txt is a legacy supplement. Its unique value is mostly per-node hostnames that change over time. The WNS entries can plausibly delay or break push notifications for Store, Mail, Teams and Outlook apps, although I found no explicit report of that.
- WSB extra.txt and update.txt are "break Windows" lists and should not be subscribed to on shared networks.

### Gaps
- There is no maintainer statement declaring the data deprecated. The only public signals are the silence since 2022 and HaGeZi's "discontinued" description.
- I could not determine the exact date AdGuard removed filter_23 from the catalog, because HostlistsRegistry history was squashed on 2026-06-27.

## Q2. HaGeZi native.* lists (native.winoffice and the device/vendor lists)

### Takeaway
HaGeZi `native.winoffice` ("Microsoft (Windows, Office, MSN)") is the best-maintained Microsoft telemetry list in 2026. It has 388 wildcard entries, rebuilt several times a day (last modified 2026-09-18), and is GPL-3.0. It is published in Adblock (`||domain^`, directly usable in ABP, uBO, AdGuard, AGH and Pi-hole v6), dnsmasq, wildcard, domains-only and RPZ formats. Hosts format has moved to the separate `dns-blocklists-legacy` repo. It is tuned to avoid Windows Update, Store, sign-in and Office breakage. Its known side effects are documented in `share/microsoft.txt`: Spotlight, Xbox achievements, Timeline or activity history, Quick Assist, location and Azure App Insights portal views.

### Cited Findings
- **Native-tracker philosophy.** Per the README, the native lists "can occasionally limit functionality". They are folded into the main tiers at four strengths:
  - Light and Normal: "Only native trackers that won't break functionality".
  - Pro: blocks more.
  - Pro++: "blocks nearly all … might cause some restrictions".
  - Ultimate: "blocking all native trackers".

  — [HaGeZi README #native](https://github.com/hagezi/dns-blocklists#native)
- **Measured tier coverage of the 388 winoffice entries (2026-09-25 builds):** Light 31, Normal 99, Pro 340, Pro++ 371, Ultimate 387. Only Ultimate blocks the `events.data.microsoft.com` family (`v10`, `v20`, `self`) and `settings-win.data.microsoft.com`. Pro++ blocks `mobile.events…` and `umwatson.events…` but not `v10` or `v20`. — computed from [adblock/pro.plus.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/pro.plus.txt), [adblock/ultimate.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/ultimate.txt) and the related tier files
- **Header (adblock build).** Title "HaGeZi's Microsoft Tracker"; "Last modified: 18 Sep 2026 22:02 UTC"; "Number of entries: 388"; "Expires: 8 hours"; "Syntax: AdBlock". — [adblock/native.winoffice.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.winoffice.txt)
- **Verified raw URLs for native.winoffice:**
  - Adblock (ABP, uBO, AGH, Pi-hole v6): `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.winoffice.txt` (CDN: `https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/native.winoffice.txt`)
  - dnsmasq: `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/dnsmasq/native.winoffice.txt`
  - Wildcard with asterisk: `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/native.winoffice.txt`
  - Wildcard domains only: `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/native.winoffice-onlydomains.txt`
  - RPZ: `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/rpz/native.winoffice.txt`
  - Hosts (legacy repo): `https://raw.githubusercontent.com/hagezi/dns-blocklists-legacy/main/hosts/native.winoffice.txt` (748 expanded entries) and `…/hosts/native.winoffice-compressed.txt` (84 entries)
  - AdGuard Home catalog mirror: `https://adguardteam.github.io/HostlistsRegistry/assets/filter_63.txt` (modified 2026-09-19)

  The old paths `…/main/hosts/native.winoffice.txt` and `…/main/domains/native.winoffice.txt` now return **404**. — [README format table](https://github.com/hagezi/dns-blocklists#native); [legacy repo](https://github.com/hagezi/dns-blocklists-legacy); [filter_63](https://adguardteam.github.io/HostlistsRegistry/assets/filter_63.txt)
- **Formats policy.** "The legacy Subdomains and Hosts formats live in a separate repository". The README lists Adblock format for "Pi-hole, AdGuard, AdGuard Home, eBlocker, uBlock Origin, Brave …". The FAQ labels Adblock "(Pi-hole v6+, TechnitiumDNS, etc.)". — [README](https://github.com/hagezi/dns-blocklists/blob/main/README.md); [FAQ](https://github.com/hagezi/dns-blocklists/blob/main/FAQ.md)
- **Composition of the adblock build by registrable domain:** live.com 92, msn.com 75, trafficmanager.net 50, microsoft.com 39, windows.net 38, msedge.net 26, bing.com 8, applicationinsights.io 7, plus azure, xbox.com and xboxlive.com. Notable entries:
  - `||events.data.microsoft.com^`, `||vortex.data.microsoft.com^`, `||telemetry.microsoft.com^` (wildcards)
  - `||telem-edge.smartscreen.microsoft.com^`, `||clarity.microsoft.com^`
  - `||activity.windows.com^`, `||arc.msn.com^`
  - Office `*-telemetry.officeapps.live.com`, `nexus(rules).officeapps.live.com`, `measure.office.com/.net`, `diagnostics.office.com`
  - Bing ads and telemetry: `ads.bing.com`, `bat.bing.com`, `c.bing.com`
  - `*-ring.msedge.net`, `fp.msedge.net`
  - Xbox telemetry: `c.xbox.com`, `beacons.xboxlive.com`

  — computed from [adblock/native.winoffice.txt](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.winoffice.txt)
- **What it avoids.** In my 31-domain "functional" test set, native.winoffice blocked none of the Windows Update, Store, activation, login, Xbox auth, Teams, Outlook, OneDrive, NCSI, CRL, `time.windows.com` or `go.microsoft.com` endpoints. The only hit was `s-ring.msedge.net`, a measurement ring host. It also does **not** block SmartScreen `nav.smartscreen…`, `wdcp`, `ecs.office.com`, `config.edge.skype.com`, the MSN/Edge new-tab (`ntp.msn.com`, `assets.msn.com`) or `copilot.microsoft.com`. — computed
- **Documented side effects (`share/microsoft.txt`, which lists domains to unblock):**
  - `arc.msn.com`: Windows Spotlight/Search and Xbox Game Pass images/perks.
  - `self.events.data.microsoft.com`: "could disrupt the ability to save documents to the cloud or access recently used files" in M365.
  - `v10/v20.events.data.microsoft.com`: Xbox Live achievements.
  - `activity.windows.com`: Timeline, and "may break Authenticator app's Cloud backup feature on Android".
  - `js.monitor.azure.com`: breaks Quick Assist.
  - `settings(-win).data.microsoft.com`: unconfirmed reports of time sync and Known Game List issues.
  - `applicationinsights.io` and `api.applicationinsights.azure.com`: Azure portal App Insights.
  - `v10c.events.data.microsoft.com`: Defender for Endpoint (a security issue if blocked).
  - `inference.location.live.net`: location services.
  - `mobile.events.data.microsoft.com`: unconfirmed Android SSO reports.
  - `browser.events.data.microsoft.com`: prevents the Visual Studio Installer download.

  — [share/microsoft.txt](https://github.com/hagezi/dns-blocklists/blob/main/share/microsoft.txt); FAQ: Ultimate "can affect things like Windows Spotlight and Xbox Live Achievements Activity History" — [FAQ](https://github.com/hagezi/dns-blocklists/blob/main/FAQ.md)
- **Scope decisions.** Issue #8071 (2025-11-20) asked HaGeZi to add 13 BSI (German federal IT security office) SiSyPHuS Windows 10 telemetry domains. It was closed "not planned". — [Issue #8071](https://github.com/hagezi/dns-blocklists/issues/8071)
- **Other native.* lists (adblock builds, 2026-09-25).** Each also exists in `dnsmasq/`, `wildcard/`, `wildcard/*-onlydomains` and `rpz/`, following the same pattern.

  | List | Entries | Last modified |
  |---|---|---|
  | native.apple | 109 | 20 Sep 2026 |
  | native.samsung | 200 | 23 Sep |
  | native.xiaomi | 345 | 11 Sep |
  | native.tiktok | 436 | 18 Sep |
  | native.tiktok.extended ("Aggressive") | 613 | 18 Sep |
  | native.lgwebos | 229 | 23 Sep |
  | native.amazon | 371 | 18 Sep |
  | native.oppo-realme | 486 | 17 Sep |
  | native.vivo | 234 | 18 Sep |
  | native.roku | 73 | 24 Sep |
  | native.huawei | 135 | 11 Sep |

  URL pattern: `https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.<name>.txt`. — [README native table](https://github.com/hagezi/dns-blocklists#native); fetched files e.g. [native.apple](https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/native.apple.txt)
- **Availability elsewhere.** AdGuard DNS offers "Native Tracker (Apple, OPPO & Realme, Samsung, Vivo, Windows/Office, Xiaomi)". The AdGuard Home catalog carries the Windows/Office (63), Apple (67), Samsung (61), Xiaomi (60), Vivo (65) and OPPO/Realme (66) lists. — [README AdGuardDNS section](https://github.com/hagezi/dns-blocklists#adguarddns); [HostlistsRegistry filters.json](https://adguardteam.github.io/HostlistsRegistry/assets/filters.json)
- **License.** GPL-3.0, and "A copy of the license … has to accompany any redistribution". — [README disclaimer](https://github.com/hagezi/dns-blocklists/blob/main/README.md)
- **Maintenance.** The repo HEAD commit is 2026-09-25 11:24 +0200. Lists are rebuilt every few hours, and `Expires: 8 hours` appears in the header. — shallow clone of [hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists)

### Inferences
- For leptest/adblock-list, HaGeZi native.winoffice is already in ABP `||domain^` syntax and can be referenced, or recommended as a companion subscription, without conversion. Copying its entries into the user's list would pull in GPL-3.0 obligations.
- A user on HaGeZi Pro gets about 88% of winoffice, and one on Pro++ about 96%. Adding native.winoffice on top matters mostly for Light, Normal, OISD, StevenBlack or AdGuard-default users.
- The documented unblock list in `share/microsoft.txt` is a ready-made "what it breaks" map. It could be mirrored as `@@` exceptions or comments in a Microsoft section of the user's list.

### Gaps
- I did not find HaGeZi's exact per-source provenance for winoffice. A DeepWiki summary mentions Vortex/Aria, App Insights, Watson and Office telemetry sources, but that site is a secondary aggregator.
- I did not verify the "~17,000 expanded domains" figure from DeepWiki. The legacy hosts build has 748 entries.

## Q3. Other lists (general and Microsoft-specific): formats, size, license, freshness, Microsoft coverage and what they break

### Takeaway
General-purpose lists (StevenBlack, OISD, AdGuard DNS/Tracking, 1Hosts Lite, EasyPrivacy, Frogeye, Disconnect) block only a handful of Microsoft telemetry hosts, typically `browser.pipe.aria`, `watson.telemetry`, `c.bing.com` and `nexus.officeapps`. 1Hosts Xtra and the 4PDA/schakal list go further. The maintained Microsoft-specific alternatives are:
- **celenity BadBlock "Microsoft"**: ABP, GPL-3.0+, about 468 rules. It is more aggressive than HaGeZi (SmartScreen, Copilot, ECS, MSN NTP) but spares core services.
- **privacyfilters "Microsoft-Blocker"**: ABP and hosts, GPL-3.0. It blocks the whole `microsoft.com`, `live.com`, `office.com` and `xboxlive.com` domains, with a small allowlist for Update, Defender and winget. It breaks sign-in, Office, Teams, Store, Xbox and activation by design.
- **BSI-derived lists** (pschneider1968, winkler-winsen) and **kevle1**: small and slow-moving.

notracking is shut down, since June 2023. Energized was revived as an aggregator whose downloads were unreachable from here.

### Cited Findings

**General lists: headers, sizes, licenses and freshness (fetched 2026-09-25)**
- **StevenBlack unified hosts (base):** `https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts`. 76,510 domains; dated 23 Sep 2026; MIT. The extensions are fakenews, gambling, porn and social only; there is no Microsoft/telemetry extension (the README's only Windows-related source is FadeMind UncheckyAds). Microsoft hits in my test set: `watson.telemetry`, `browser.pipe.aria`, `nexus.officeapps`, `c.bing.com`. — [hosts](https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts); [readme](https://github.com/StevenBlack/hosts/blob/master/readme.md); [license](https://github.com/StevenBlack/hosts/blob/master/license.txt)
- **AdGuard DNS filter:** `https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt`. About 182k rules; modified 2026-09-25; GPL-3.0. It is "composed of several other filters (AdGuard Base filter, Tracking Protection filter, … EasyPrivacy …) simplified … for DNS-level". Microsoft hits: `vortex.data.microsoft.com`, `browser.pipe.aria`, `browser.events.data.msn.com`, `c.msn.com`. — [filter.txt](https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt); [LICENSE](https://github.com/AdguardTeam/AdGuardSDNSFilter/blob/master/LICENSE)
- **AdGuard Tracking Protection filter (formerly "Spyware filter"; source directory `SpywareFilter/`):** `https://filters.adtidy.org/extension/ublock/filters/3.txt` (uBO) or `…/chromium/filters/3.txt`. ABP/AdGuard syntax; TimeUpdated 2026-09-25; GPL-3.0. Microsoft DNS-level hits: `browser.pipe.aria`, `browser.events.data.msn.com`, `c.msn.com`. — [filters/3.txt](https://filters.adtidy.org/extension/ublock/filters/3.txt); [AdguardFilters LICENSE](https://github.com/AdguardTeam/AdguardFilters/blob/master/LICENSE)
- **1Hosts Lite and Xtra:** `https://badmojr.github.io/1Hosts/Lite/adblock.txt` (about 102k) and `https://badmojr.github.io/1Hosts/Xtra/adblock.txt` (about 786k). Also available as hosts, domains, wildcards, dnsmasq, RPZ, unbound and hosts.win. Last modified 2026-09-03; MPL-2.0.
  - Lite blocks `v20/mobile/umwatson.events`, `watson/oca.telemetry`, `browser.pipe.aria`, `dc.services.visualstudio.com`, `c.bing.com` and `fp.msedge.net`.
  - Xtra additionally blocks the whole `events.data.microsoft.com` family, `nexus.officeapps`, `c.msn.com` and `ris.api.iris.microsoft.com` (Spotlight).

  — [1Hosts repo](https://github.com/badmojr/1Hosts); [Lite/adblock.txt](https://badmojr.github.io/1Hosts/Lite/adblock.txt); [LICENSE](https://github.com/badmojr/1Hosts/blob/master/LICENSE)
- **OISD small and big:** `https://small.oisd.nl` (56,386) and `https://big.oisd.nl` (243,922). ABP `||x^` syntax (`/domainswild` and other variants exist); rebuilt hourly (modified 2026-09-25); GPL-3.0; motto "Block. Don't break." Microsoft hits: big blocks `oca.telemetry` and `c.bing.com`; small blocks none of my test telemetry domains. — [big.oisd.nl](https://big.oisd.nl); [LICENSE](https://github.com/sjhgvr/oisd/blob/main/LICENSE)
- **Frogeye first-party and multi-party trackers:** `https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt` (about 14.5k lines; generated 2026-09-20; MIT) and `…/multiparty-trackers-hosts.txt`. These are CNAME-cloaking trackers with **zero** Microsoft test-set hits. — [frogeye](https://hostfiles.frogeye.fr/firstparty-trackers-hosts.txt); [LICENSE](https://git.frogeye.fr/geoffrey/eulaurarien/src/branch/master/LICENSE)
- **EasyPrivacy (Firebog mirror):** `https://v.firebog.net/hosts/Easyprivacy.txt` (43k; "Updated 23SEP26"). Microsoft hits: `vortex.data.microsoft.com`, `browser.pipe.aria`. — [Easyprivacy.txt](https://v.firebog.net/hosts/Easyprivacy.txt)
- **Disconnect simple_tracking:** `https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt`. Only 38 lines; Firebog marks Disconnect with a cross (not recommended); no Microsoft hits. — [simple_tracking.txt](https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt); [firebog.net](https://firebog.net/)
- **4PDA / schakal hosts:** `https://schakal.ru/hosts/alive_hosts_ru_com.txt` (about 105k) and `https://schakal.ru/hosts/hosts_mail_fb.txt` ("Records: 268490"; modified 24 Sep 2026; hosts format). It is aggressive on Microsoft telemetry: `v10`, `v20`, `mobile` and `umwatson.events`, `settings-win.data`, `watson/oca.telemetry`, `browser.pipe.aria`, `nexus.officeapps`, `dc.services.visualstudio.com` and `fp.msedge.net` are all blocked. None of the functional test domains are blocked. Blocking `v10.events` and `settings-win` breaks Xbox achievements (see HaGeZi's notes). — [schakal hosts](https://schakal.ru/hosts/hosts_mail_fb.txt)
- **Blocklist Project "tracking":** `https://blocklistproject.github.io/Lists/tracking.txt` (143,876; modified 2026-07-18; MIT). It blocks many Microsoft telemetry hosts including `activity.windows.com`, `arc.msn.com`, `settings-win`, `vortex-win` and `self.events`. It also blocks `s-ring.msedge.net`. — [tracking.txt](https://blocklistproject.github.io/Lists/tracking.txt)
- **DandelionSprout.** There is no Microsoft-telemetry list. The "Game Console Adblock List" (`https://raw.githubusercontent.com/DandelionSprout/adfilt/master/GameConsoleAdblockList.txt`; AGH catalog id 6) contains Xbox entries: `arc.msn.com` scoped `$ctag=~device_pc|~os_windows`, `rad.msn.com` and `nw-umwatson.events.data.microsoft.com`. It notes that blocking `arc.msn.com` kills Game Pass Perks. — [GameConsoleAdblockList.txt](https://raw.githubusercontent.com/DandelionSprout/adfilt/master/GameConsoleAdblockList.txt)
- **Perflyst PiHoleBlocklist.** SmartTV (`…/master/SmartTV.txt`, 630 lines; AGH version `SmartTV-AGH.txt`), `android-tracking.txt`, `AmazonFireTV.txt` and `SessionReplay.txt`. MIT; repo last commit 2026-09-09. There is no Microsoft/Windows list and no Microsoft entries in SmartTV or Android. Firebog lists all three Perflyst lists with a **cross**. — [PiHoleBlocklist](https://github.com/Perflyst/PiHoleBlocklist); [firebog.net](https://firebog.net/)
- **notracking/hosts-blocklists: SHUT DOWN.** The README says "The NoTracking blocklist will be shutting down soon" (issue #900). The last hostnames.txt update is "Mon Jun 26 13:29:58 CEST 2023" and the last commit is 2023-06-26. License CC BY-NC-SA 4.0. — [notracking README](https://github.com/notracking/hosts-blocklists); [issue #900](https://github.com/notracking/hosts-blocklists/issues/900)
- **Energized Protection: revived as an aggregator.** The GitHub repo `EnergizedProtection/block` now holds only `config.json` and the readme. It auto-commits daily (2026-09-25, v0.100.a, "alpha"). Packs spark, blu and ultimate are served from `https://energized.pro/<pack>/…`, but those downloads returned 502 via this session's proxy. The old `…/master/spark/formats/hosts.txt` path is 404. Its sources include WindowsSpyBlocker spy.txt, the AdGuard Tracking Protection sections and several HaGeZi native lists (but not winoffice). License MIT. — [EnergizedProtection/block](https://github.com/EnergizedProtection/block)
- **NextDNS native-tracking-domains:** `https://raw.githubusercontent.com/nextdns/native-tracking-domains/main/domains/windows`. 23 domains (vortex, telemetry, settings-win, watson, feedback, `spynet2`, onecollector, and others). Last commit 2023-01-25, so stale. — [nextdns/native-tracking-domains](https://github.com/nextdns/native-tracking-domains)
- **jmdugan corporations/microsoft/all:** `https://raw.githubusercontent.com/jmdugan/blocklists/master/corporations/microsoft/all`. 960 lines; last commit 2024-10-31. It blocks entire corporate domains (`windowsupdate.com`, `update.microsoft.com`, `xboxlive.com`, `a-msedge.net`, `go.microsoft.com`, `account.microsoft.com`, `1drv.com`) and breaks everything Microsoft. — [jmdugan/blocklists](https://github.com/jmdugan/blocklists)

**Microsoft-specific lists**
- **celenity BadBlock "Microsoft" (Codeberg, mirrored on GitLab and GitHub):**
  - ABP: `https://badblock.celenity.dev/abp/microsoft.txt` (alternates: `https://codeberg.org/celenity/BadBlock/raw/branch/pages/abp/microsoft.txt`, `https://raw.githubusercontent.com/celenityy/BadBlock/pages/abp/microsoft.txt`)
  - Wildcards: `…/wildcards-star/microsoft.txt` and `…/wildcards-no-star/microsoft.txt`

  Header "🪟 BadBlock - Microsoft (ABP)", Version 17May2026v1, "Expires: 1 hour"; 468 `||` rules, 58 of which are path rules (e.g. `||live.com/ows/v*/OutlookOptions/AdsAggregate`) that DNS blockers will ignore or skip. GPL-3.0-or-later; repo updated 2026-09-21. It deliberately blocks SmartScreen ("extremely invasive from a privacy perspective"), plus `copilot.microsoft.com`, `ecs.office.com`, `ntp.msn.com`, `wdcp.microsoft.com` and `c.msn.com`. No functional test-set domains are blocked apart from `s-ring.msedge.net`. The list is included in BadBlock Lite, BadBlock and BadBlock+. — [BadBlock README](https://codeberg.org/celenity/BadBlock); [abp/microsoft.txt](https://codeberg.org/celenity/BadBlock/raw/branch/pages/abp/microsoft.txt)
- **privacyfilters "Microsoft-Blocker" (Codeberg primary, GitHub mirror):**
  - Proper, ABP: `https://codeberg.org/privacyfilters/Microsoft-Blocker/raw/branch/main/adblock_dns_proper.txt` (1,289 entries; v1.80; last modified 14 May 2026)
  - Proper as hosts, domains and hosts-clean: `…/hosts`, `…/domains.txt`, `…/hosts-clean`
  - "No Microsoft Edition": `…/adblock_dns_nomicrosoft.txt` and `…/hosts_nomicrosoft`

  GPL-3.0; last commit 2026-05-15. It blocks the root domains `microsoft.com`, `live.com`, `office.com`, `windows.com`, `msn.com`, `bing.com`, `skype.com`, `xboxlive.com`, `windowsupdate.com` and `msftconnecttest.com`, then re-allows with 27 `@@` rules: `update.microsoft.com`, `delivery.mp.microsoft.com`, `windowsupdate.com`, `msftconnecttest.com`, `smartscreen`, `wdcp`, `crl`, `oneocsp`, `definitionupdates`, `cdn.winget`, `go.microsoft.com`, `fs.microsoft.com`, and others. The README warns it "can cause some microsoft services not to work properly". The author doesn't use Microsoft products, and the README points "minimal tracking protection" users to HaGeZi native Microsoft and BadBlock Microsoft. — [Microsoft-Blocker README](https://codeberg.org/privacyfilters/Microsoft-Blocker)
- **pschneider1968/pihole-bl-msft-telemetry-bsi:** `https://raw.githubusercontent.com/pschneider1968/pihole-bl-msft-telemetry-bsi/master/msft_telemetry_bsi.txt`. 73 non-comment lines covering the `events.data`, `vortex(-win)`, `settings-win`, `watson` and `telecommand` families from the BSI SiSyPHuS Win10 analyses (builds 1809 and 21H2). Last commit 2026-07-31. The README says "This version is for Pi-Hole 5.x … not tested with Pi-Hole 6.x", and its refresh script "will completely replace all blacklist and whitelist entries" in Pi-hole. — [repo README](https://github.com/pschneider1968/pihole-bl-msft-telemetry-bsi)
- **winkler-winsen/microsoft-telemetry-blocklist-BSI-:** single file `ms-win10-telemetry-blocklist.txt`; last commit 2023-03-08, so stale. — [repo](https://github.com/winkler-winsen/microsoft-telemetry-blocklist-BSI-)
- **kevle1/windows-telemetry-blocklist:** `https://raw.githubusercontent.com/kevle1/windows-telemetry-blocklist/master/windowsblock.txt`. 157 non-comment lines; last commit 2024-06-05. It blocks `v10/v20.events`, `settings-win`, `vortex` and `wdcp`. — [repo](https://github.com/kevle1/windows-telemetry-blocklist)
- **gurkensalat/pi-hole-blocklist** ("Block Windows 10 telemetry with pi-hole"): last commit 2021-02-01, so stale. — [repo](https://github.com/gurkensalat/pi-hole-blocklist)
- **W4RH4WK/Debloat-Windows-10 `scripts/block-telemetry.ps1`:** a PowerShell script that writes a hosts file and firewall rules; it is not a subscribable list. Repo last commit 2025-09-23. — [block-telemetry.ps1](https://github.com/W4RH4WK/Debloat-Windows-10/blob/master/scripts/block-telemetry.ps1)
- **niutech Edge-tracking hosts gist:** exists, but I did not verify its contents or date. — [gist](https://gist.github.com/niutech/1f1c1518ce0eba7e8d429c812d39493d)

**Coverage matrix: telemetry test set**

"Hit" means blocked. The five selected telemetry hosts are v10.events, settings-win, SmartScreen `nav.`, `ntp.msn.com` and `copilot`. Each non-dash cell lists the hosts that list blocks; a dash means it blocks none of them. The functional column shows how many of the 31 functional endpoints (Windows Update, Store, activation, sign-in, Xbox, Teams, Outlook, OneDrive, NCSI, CRL, time) are hit.

| List | Telemetry hits (of 31) | Selected hosts blocked | Functional hits (of 31) |
|---|---|---|---|
| WSB spy | 7 | – | 0 |
| WSB extra | 20 | v10, settings-win, nav, ntp | 18 (breaks sign-in, NCSI, activation, Outlook, OneDrive, Store) |
| HaGeZi winoffice | 18 | v10 | 1 (s-ring) |
| HaGeZi Ultimate | 19 | v10, settings-win | 1 |
| BadBlock Microsoft | 27 | v10, settings-win, nav, ntp, copilot | 1 |
| Microsoft-Blocker proper | effectively all | all five | root blocks with Update, NCSI and CRL re-allowed; login, Teams, Outlook, OneDrive, Store and activation still blocked |
| 1Hosts Xtra | 16 | v10 | 0 |
| schakal | 13 | v10, settings-win | 0 |
| StevenBlack | 4 | – | 0 |
| OISD big | 2 | – | 0 |
| AdGuard DNS | 4 | – | 0 |

— computed from the raw files cited above

### Inferences
- For ABP-syntax consumers, three lists are ready to subscribe with no conversion: HaGeZi `adblock/native.winoffice.txt` (balanced), BadBlock `abp/microsoft.txt` (stricter, and adds SmartScreen, Copilot and MSN NTP), and Microsoft-Blocker `adblock_dns_proper.txt` (nuclear). All three are GPL-3.0, which matters if the user copies entries into a list under a different license. WindowsSpyBlocker is MIT but is hosts-only and stale.
- Blocking `settings-win.data.microsoft.com` or the `events.data.microsoft.com` family is the main dividing line between "safe" lists and "strict" lists. HaGeZi keeps them out of Light, Normal, Pro and Pro++ but has them in winoffice and Ultimate. BadBlock, schakal and 1Hosts Xtra block them. They are tied to Xbox achievements, M365 recent files and cloud save, and Defender for Endpoint (`v10c`).

### Gaps
- I could not fetch Energized pack files (proxy 502), so their current Microsoft coverage is unverified.
- The winkler-winsen list content and size were not fetched. I checked only the file listing and date.
- An "MS-Office-Telemetry"-named standalone list was not found. Office telemetry is covered inside HaGeZi winoffice and BadBlock Microsoft.
- Whether Pi-hole v6 honours `@@||domain^` exception lines inside a subscribed blocklist (relevant to Microsoft-Blocker proper) was not verified. If it does not, Microsoft-Blocker would also block Windows Update under Pi-hole.
- I found no filterlists.com data. I did not query it, having prioritized primary sources.

## Q4. What the Pi-hole, AdGuard and uBlock communities recommend for Microsoft telemetry in 2025-2026

### Takeaway
The recommendations have split:
- **Firebog** (the classic Pi-hole reference) still green-ticks WindowsSpyBlocker spy.txt.
- **The AdGuard Home catalog and AdGuard DNS** have replaced it with HaGeZi's Windows/Office Tracker list.
- **Privacy communities** (Privacy Guides forum; Microsoft-Blocker's own README) point to HaGeZi native.winoffice, or HaGeZi Pro++ or Ultimate, for balanced blocking. BadBlock Microsoft or Microsoft-Blocker are for stricter blocking.

I found no official Pi-hole or uBlock Origin team recommendation specific to Microsoft telemetry.

### Cited Findings
- Firebog lists "Crazy Max's Microsoft Telemetry" (WSB spy.txt) with a tick, meaning "least likely to interfere with browsing". Firebog's page does not mention HaGeZi native lists. — [firebog.net](https://firebog.net/)
- The AdGuard Home built-in catalog includes "HaGeZi's Windows/Office Tracker Blocklist" (id 63, updated 2026-09-19) and no WindowsSpyBlocker entry. HaGeZi's registry request framed winoffice as the successor to the "discontinued" WSB list. — [filters.json](https://adguardteam.github.io/HostlistsRegistry/assets/filters.json); [HostlistsRegistry #507](https://github.com/AdguardTeam/HostlistsRegistry/issues/507)
- AdGuard DNS offers HaGeZi Native Tracker Windows/Office as a selectable list. — [HaGeZi README](https://github.com/hagezi/dns-blocklists#adguarddns)
- HaGeZi's own guidance: native trackers are "already baked in" to the tiers. Users who want full native coverage without Ultimate should "add the specific device lists you actually need on top of your current tier". — [FAQ](https://github.com/hagezi/dns-blocklists/blob/main/FAQ.md)
- Privacy Guides forum (Nov 2025): posters questioned WSB's staleness and suggested HaGeZi native.winoffice or Ultimate. — [Privacy Guides thread](https://discuss.privacyguides.net/t/windows-spyblocker-still-good-in-2025/32656)
- Microsoft-Blocker's README: "If you only need minimal tracking protection, you should use Hagezi's Native Trackers:Microsoft and celenity's Badblock Microsoft individual list." It also says hosts files and in-OS adblockers are "only partially effective", because "Microsoft can ignore/bypass them", and recommends network-wide DNS. — [Microsoft-Blocker](https://codeberg.org/privacyfilters/Microsoft-Blocker)
- Older Pi-hole Discourse threads ("Windows 10 Spying & Telemetry Blocking", "Blocking Microsofts Telemtry") historically pointed to WindowsSpyBlocker. I did not read them in full this session. — [Discourse 8001](https://discourse.pi-hole.net/t/windows-10-spying-telemetry-blocking/8001); [Discourse 28295](https://discourse.pi-hole.net/t/blocking-microsofts-telemtry/28295)

### Inferences
- A defensible 2026 recommendation for Pi-hole, AGH and ABP users is a general list plus HaGeZi `native.winoffice`, with BadBlock Microsoft as an optional strict add-on and WSB spy.txt as optional legacy. Avoid WSB extra and update, jmdugan and Microsoft-Blocker unless the machine is intentionally cut off from Microsoft services.
- Firebog's continued tick for WSB reflects low breakage rather than freshness.

### Gaps
- I did not retrieve Reddit r/pihole or r/privacy threads from 2025-2026, as search results did not surface them, so there are no Reddit citations.
- There is no official statement from the Pi-hole team or from uBlock Origin's maintainers on Microsoft telemetry lists. uBO's default lists (EasyPrivacy, uBO Privacy) cover only a few Microsoft hosts at the DNS level.
