# Consumer and ISP Router "Phone Home" / Telemetry Behavior and How to Stop It

Research date: 2026-09-25. About 24 search and fetch calls. Several vendor forums (SNBForums, Ubiquiti Community) returned 403 errors or loaded no content, so some vendor domain lists are thin. Those gaps are marked below.

## 1. Per-vendor catalog: what routers send home, and the domains involved

### Takeaway
Every major consumer router vendor collects some device or network telemetry. The vendors split into two groups:
- **Cloud-mandatory:** eero and Google Nest Wifi. The only way to stop the collection is to stop using the product.
- **Opt-out, with degraded features:** Netgear, ASUS, TP-Link and UniFi.

The biggest privacy exposure is not basic telemetry. It is the "security" add-ons (ASUS AiProtection/Trend Micro, Netgear Armor/Bitdefender), which check the URLs or domains you visit against a vendor cloud. Only Netgear, TP-Link and Ubiquiti have source-backed domain lists. ASUS, Linksys, Google, eero and the ISP gateways do not.

### Cited Findings

**Netgear (Nighthawk, Orbi, Armor)**
- **History:** Netgear added "Router Analytics Data Collection" to routers via a firmware update in May 2017, starting with the Nighthawk R7000. To disable it, go to Advanced → Administration → Router Update → Router Analytics Data Collection → Disable — [Pi-hole Discourse (2017-05-22)](https://discourse.pi-hole.net/t/netgear-now-collects-router-analytics-data-here-are-the-steps-to-disable-it/3306); [The Hacker News](https://thehackernews.com/2017/05/netgear-router-analytics-data.html); [BleepingComputer](https://www.bleepingcomputer.com/news/hardware/netgear-enables-user-data-collection-feature-on-popular-router-model/)
- **Data categories collected**, per Netgear's Analytics Data Policy (last updated 2020-10-30):
  - Identifiers: IP address, device/serial number
  - Geolocation: device location, city, ISP
  - Inferences: electronic network info for diagnostics
  - Language preferences
  - Usage analytics, hardware analytics, wireless information and engineering quality metrics

  — [NETGEAR Analytics Data Policy](https://www.netgear.com/about/analyticsdatapolicy/)
- **Opting out:**
  - The policy's opt-out is an email to analyticspolicy@netgear.com.
  - Netgear warns that opting out "will restrict our ability to warn you of security issues about your device" and may end trial or paid subscriptions.

  — [NETGEAR Analytics Data Policy](https://www.netgear.com/about/analyticsdatapolicy/)
- **In-app opt-out by region:** Netgear's support KB documents an in-app/router opt-out only for accounts in the EU or UK (Nighthawk/Orbi: Settings > Data Collection). US owners are directed to the email opt-out — [NETGEAR KB 000064225](https://kb.netgear.com/000064225/I-live-in-the-European-Union-or-United-Kingdom-how-do-I-opt-out-of-NETGEAR-analytics-data-collection); [BGR](https://www.bgr.com/2257567/how-to-opt-out-netgear-router-data-collection/); [WindowsForum](https://windowsforum.com/news/netgear-router-data-opt-out-requires-email-for-u-s-owners.445065/)
- **Orbi without a toggle:** Users reported that on some Orbi models (e.g., RBR50) analytics collection was on and had no off switch — [NETGEAR Community: disable analytics on Orbi RBR50](https://community.netgear.com/discussions/Orbi/how-can-i-disable-netgear-analytics-on-orbi-rbr50/1737330)
- **Armor (Bitdefender):**
  - Armor intercepts outgoing HTTP/HTTPS requests and checks them against Bitdefender's URL-status cloud.
  - A Netgear community thread relays a Bitdefender support rep's claim that visited sites are not retained. This claim is unverified.
  - The NETGEAR Armor iOS app's privacy label lists Browsing History, Usage Data and Diagnostics.

  — [NETGEAR Community: Armor and Privacy](https://community.netgear.com/discussions/en-home-armor/armor-and-privacy/2202948); [Armor app, App Store](https://apps.apple.com/us/app/-/id1322992373); [Bitdefender NETGEAR page](https://www.bitdefender.com/en-us/netgear)
- **Turning Armor off:** Armor can be toggled off in the Orbi/Nighthawk app under Settings → Security. Some users could not find the toggle at first — [NETGEAR Community: turn off Armor on Orbi](https://community.netgear.com/discussions/en-home-armor/how-do-i-turn-off-armorbitdefender-on-my-orbi-router/1733734/replies/1734652)
- **Netgear domains** observed by a user's own DNS on a Netgear router, from the anthony-wang/PiHoleBlocklist `netgear.txt` ("snooped from my Network router"). Source for every domain in this list: [anthony-wang/PiHoleBlocklist netgear.txt](https://github.com/anthony-wang/PiHoleBlocklist/blob/master/netgear.txt).
  - Telemetry, registration and cloud:
    - `registration.ngxcld.com`
    - `presence.ngxcld.com`
    - `advisor.ngxcld.com`
    - `genieremote.netgear.com` (Genie remote access)
    - `peerevent-prod.netgear.com`
    - `peernetwork.netgear.com`
    - `peernotification-prod.netgear.com`
  - Firmware updates:
    - `updates1.netgear.com`
    - `updates2.netgear.com`
    - `updates3.netgear.com`
    - `http.fw.updates1.netgear.com`
  - Cloud storage features:
    - `readycloud.netgear.com`
    - `readyshare.netgear.com`
    - The list warns that blocking these breaks ReadyCLOUD/ReadySHARE.
  - Torrent:
    - `dht.transmissionbt.com` (BitTorrent DHT, presumably from ReadySHARE/download-manager features; inference).
  - Deliberately not blocked:
    - `www.netgear.com` and `netgear.com` are commented out because the router pings them often (likely a connectivity check).
    - Blocking them would also block the vendor's website.
- **Update-query volume:** In one report, 95% of a Pi-hole's queries were to `updates1.netgear.com`.
- **Workaround on custom firmware:** SNBForums custom-firmware users traced `registration.ngxcld.com` to `/bin/datalib`, which embeds that URL, and sinkholed it in the router's hosts file — [search summary of SNBForums R7800 custom firmware thread](https://www.snbforums.com/threads/custom-firmware-build-for-r7800-v-1-0-2-67sf-1-0-2-67-1sf.56921/page-4) (page not fetched directly; treat as PLAUSIBLE).
- **`devicelocation.ngxcld.com`** (named in the task brief) did not appear in any source I retrieved. Treat it as UNVERIFIED. It fits the `*.ngxcld.com` pattern above.

**TP-Link (standalone routers, Deco, HomeShield, Omada)**
- **`tplinkcloud.com`**
  - Role: the core account and cloud API (login, remote control, push notifications).
  - Blocking it removes remote/app-over-internet access. Local LAN control is unaffected.
  - Whitelist `n-device-api.tplinkcloud.com` (device registration and re-auth).

  — [sappafrancesco/dns-blocklists TP-Link README](https://github.com/sappafrancesco/dns-blocklists/blob/main/vendors/tplink/README.md)
- **`tplinknbu.com`**
  - Role: the Tapo/IoT backend (camera relay, cloud storage, telemetry, Omada check-in).
  - Whitelist `security.iot.i.tplinknbu.com` (camera auth). Blocking it together with `n-device-api.tplinkcloud.com` was reported to lock a camera out completely.

  — [same](https://github.com/sappafrancesco/dns-blocklists/blob/main/vendors/tplink/README.md)
- **Other TP-Link domains:**
  - `tplinkdns.com` is the free DDNS service. It is safe to block if you don't use it.
  - `tplinklogin.net` is a local alias for the router's admin page. It is safe to block; use the IP instead.

  — [same](https://github.com/sappafrancesco/dns-blocklists/blob/main/vendors/tplink/README.md)
- **Omada:**
  - `n-devs-smb.tplinkcloud.com` and `n-deventry-smb.tplinkcloud.com` are the Omada SDN controller's cloud check-in and telemetry endpoints. Users say these phone home even in local-only setups.
  - TP-Link shipped an option on EAP/Omada devices in June 2022 to disable "cloud connection behavior".
  - DNS-blocking can make the Omada UI show false "device disconnected" states.

  — [search summary of the sappafrancesco TP-Link README](https://github.com/sappafrancesco/dns-blocklists/blob/main/vendors/tplink/README.md) (the direct fetch did not show these hostnames; treat as PLAUSIBLE)
- **`www.tp-link.com` query volume:** A TP-Link router was seen querying `www.tp-link.com` about 4 times a minute. It was not NTP, DDNS or remote access, and the cause was never resolved. This is most likely a connectivity check (inference) — [pi-hole/pi-hole issue #2982](https://github.com/pi-hole/pi-hole/issues/2982)
- **US government status:**
  - **Late 2024:** Commerce, Defense and Justice opened investigations — [The Register, 2024-12-18](https://www.theregister.com/2024/12/18/us_govt_probes_tplink_routers/)
  - **October 2025:** An interagency assessment led by Commerce backed a ban on new sales — [Washington Post, 2025-10-30](https://www.washingtonpost.com/technology/2025/10/30/tp-link-proposed-ban-commerce-department/)
  - **Early 2026:** The White House reportedly shelved the federal ban ahead of a Trump–Xi summit — [9to5Mac, 2026-02-18](https://9to5mac.com/2026/02/18/federal-ban-on-tp-link-routers-shelved-but-texas-fights-on/)
  - **Texas:**
    - The Texas AG opened an investigation in October 2025 and sued TP-Link Systems in February 2026 for deceptive security marketing.
    - Governor Abbott banned TP-Link on state employee devices in January 2026.

    — [9to5Mac](https://9to5mac.com/2026/02/18/federal-ban-on-tp-link-routers-shelved-but-texas-fights-on/)
  - **Market share:** 9to5Mac cites TP-Link at about 65% of the US market, rebranded by more than 300 ISPs — [9to5Mac](https://9to5mac.com/2026/02/18/federal-ban-on-tp-link-routers-shelved-but-texas-fights-on/)
  - **Mid-2026:** One aggregator says a broader Commerce ban was "proposed, not final" as of mid-2026. This is a low-quality source and unconfirmed — [smarthomeperfected](https://www.smarthomeperfected.com/is-tp-link-safe/)
  - **Conflict:** The WaPo "ban warranted" report and the 9to5Mac "shelved" report are sequential, not contradictory. I found no primary source for a final ruling as of September 2026.

**ASUS (AiProtection / Trend Micro)**
- **What ASUS collects:** IP, hashed MAC, country of manufacture, model, firmware/module versions, manufacture date, firmware-update data, system status, boot info, network connection details, crash history and security events — [ASUS Privacy Policy (search summary)](https://www.asus.com/terms_of_use_notice_privacy_policy/privacy_policy/); discussed at [SNBForums: ASUS firmware update privacy policy](https://www.snbforums.com/threads/asus-firmware-update-privacy-policy.90257/) (SNBForums returned 403 on fetch)
- **Opting out:**
  - Sharing can be toggled at Administration → Firmware Upgrade / Privacy.
  - If you disable it you may not get firmware updates, but ASUS says critical security updates are still downloaded automatically, sending IP, hashed MAC and model.

  — [ASUS Privacy Policy (search summary)](https://www.asus.com/terms_of_use_notice_privacy_policy/privacy_policy/)
- **What Trend Micro collects via AiProtection:** "URLs, Domains and IP addresses of websites visited", MAC addresses and device IDs, public IP, suspicious-file metadata, and source/destination IPs — [MBReviews, 2021-08-02](https://www.mbreviews.com/trend-micro-aiprotection-asus/)
- **Withdrawing consent:**
  - Go to Administration → Privacy → Withdraw (Trend Micro).
  - This disables AiProtection (malicious-site blocking, two-way IPS, infected-device blocking), Traffic Analyzer, Apps Analyzer, Adaptive QoS, Game Boost and Web History.

  — [MBReviews](https://www.mbreviews.com/trend-micro-aiprotection-asus/); [MalwareTips thread](https://malwaretips.com/threads/asus-router-aiprotection-and-firewall-are-they-any-good.126154/)
- **ASUS domains:**
  - `nw-dlcdnet.asus.com` is referenced as hosting the router's EULA and privacy notices — [MalwareTips thread (search snippet)](https://malwaretips.com/threads/asus-router-aiprotection-and-firewall-are-they-any-good.126154/)
  - I did not retrieve a source confirming these as ASUS firmware-check, DDNS or telemetry endpoints, so treat them as UNVERIFIED:
    - `dlcdnets.asus.com`
    - `asusrouter.com` (believed to be the free DDNS / local alias)
    - any Trend Micro backend hostnames
  - The only Trend Micro hostname found was `trendmicro.com.edgekey.net`, mentioned in MBReviews. Its role was not confirmed — [MBReviews](https://www.mbreviews.com/trend-micro-aiprotection-asus/)

**Linksys (Smart Wi-Fi, Velop)**
- A 2026 guide says that from 2026-03-26 Linksys began ending cloud access for some EA, WHW and MX models. After the latest firmware, LinksysSmartWiFi.com no longer manages them, remote access and app setup stop, and no new cloud accounts can be created — [iTechGuides (secondary; not verified against a Linksys primary source)](https://www.itechguides.com/linksys-smart-wi-fi-tools-2026-setup-and-troubleshooting-guide/)
- No sourced Linksys telemetry domain list was found beyond `linksyssmartwifi.com`, the cloud management portal named in the source above.

**eero (Amazon)**
- **Cloud-first design:**
  - eero relies on a cloud control plane "in near constant communication" with eero servers.
  - Even per-device real-time usage is routed through the cloud.
  - Diagnostics, device lists and telemetry flow continuously whether or not the app is in use.

  — [How-To Geek, 2026-09-01](https://www.howtogeek.com/eeros-silent-cloud-syncs-are-turning-your-router-into-yet-another-tracking-device/)
- **What eero collects:** network status, IP and MAC addresses, bandwidth usage, signal strength, connected device types and temperatures — [How-To Geek](https://www.howtogeek.com/eeros-silent-cloud-syncs-are-turning-your-router-into-yet-another-tracking-device/); [eero Privacy Notice](https://eero.com/legal/privacy)
- **No opt-out:** How-To Geek quotes the eero privacy policy as saying the only way to fully stop collection is to uninstall the app and unplug every eero — [How-To Geek](https://www.howtogeek.com/eeros-silent-cloud-syncs-are-turning-your-router-into-yet-another-tracking-device/)
- **Browsing data:** eero's CEO has said eero has no capability to collect browsing data — [Fortune, 2019](https://fortune.com/2019/03/12/amazon-eero-mesh-networks-data-privacy)
- **Amazon account linking** shares your Amazon name and email with eero, and your Wi-Fi network names and passwords with Amazon — [eero Support](https://support.eero.com/hc/en-us/articles/360045529291-Amazon-Account-Linking-What-is-shared)

**Google Nest Wifi / Google Wifi**
- **Management:** These are managed only through the Google Home app.
- **Controls:** Privacy controls cover "Cloud services" and "Wifi point stats".
- **What is always kept:** The association between your Google Account and your network is stored even with all controls off.
- **Google's stated limits:** Google says the data isn't used for ad personalization and that Google Wifi does not track visited websites or traffic content.

— [Google Nest Wifi & your privacy](https://support.google.com/googlehome/answer/6246642?hl=en)

**Ubiquiti UniFi**
- **Analytics domain:** Ubiquiti's documented analytics FQDN is `trace.svc.ui.com`. It can be blocked with Pi-hole or a firewall rule.
- **UI toggle:** UniFi OS Settings → Advanced / Control Plane → "Analytics & Improvements" (Minimum / Standard / Off).
- **Limits of the toggle:** Community users report that turning it off may only reduce or anonymize data rather than stop the traffic. Setting `system.analytics.enabled=false` and `system.analytics.anonymous=false` (self-hosted controller) is described as a fuller stop.

— [UniHosted blog on UniFi privacy](https://www.unihosted.com/blog/unifi-s-internet-history-checking-information-on-privacy-and-data-handling-by-unifi); [Ubiquiti Community: Disabling trace.svc.ui.com tracking, yet again](https://community.ui.com/questions/Disabling-trace-svc-ui-com-tracking-yet-again/da39eba4-70fa-4984-9f41-66881534e09f?page=1); [UniFi Analytics cannot be disabled](https://community.ui.com/questions/UniFi-Analytics-cannot-be-disabled-whatsoever/300f6fed-118e-4cd9-9a47-d399c53483f9); [hassio-addons discussion #143](https://github.com/hassio-addons/addon-unifi/discussions/143). The Ubiquiti Community pages did not render on fetch, so this rests on search summaries.

**ISP gateways (Comcast Xfinity, AT&T BGW, Verizon Fios, Spectrum, BT, Sky, Virgin): TR-069/CWMP**
- **What TR-069 is:** TR-069 (CWMP) is a SOAP protocol. The ISP's Auto Configuration Server (ACS) uses it to configure devices remotely, push firmware and run diagnostics — [Wikipedia: TR-069](https://en.wikipedia.org/wiki/TR-069); [AVSystem crash course](https://avsystem.com/crashcourse/tr069/)
- **Can't be turned off:** Usually there is no option to disable it on ISP-supplied equipment.
- **ACS compromise risk:** A compromised ACS exposes SSIDs, MACs, VoIP credentials and admin passwords.
- **Weak transport security (2014 research):** About 80% of deployments didn't use HTTPS, and some devices accepted self-signed ACS certificates.

— [Computerworld (Check Point research, 2014)](https://www.computerworld.com/article/1525268/home-routers-supplied-by-isps-can-be-compromised-en-masse.html); [SEC Consult](https://sec-consult.com/blog/detail/tr-069-iot-before-it-was-cool/)
- **TR-069 and blocking:** The management session runs from the gateway's WAN interface to the ISP's ACS, often on a separate management VLAN or IP. It never passes through your LAN DNS or firewall, so it can't be blocked from inside. This is an inference based on how the protocol is designed.

**Existing blocklists**
- **HaGeZi native tracker lists** cover Amazon, Apple, Huawei, Microsoft, Samsung, TikTok, LG webOS, Roku, Vivo, OPPO/Realme and Xiaomi. There is **no** router-vendor list (no TP-Link, Netgear or ASUS). Native tracker coverage is also folded into each HaGeZi tier at a different strength — [hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists)
- **sappafrancesco/dns-blocklists** has a TP-Link vendor list (`tplink_block_with_whitelist.txt`) with allowlist exceptions — [README](https://github.com/sappafrancesco/dns-blocklists/blob/main/vendors/tplink/README.md)
- **anthony-wang/PiHoleBlocklist** has `netgear.txt` — [link](https://github.com/anthony-wang/PiHoleBlocklist/blob/master/netgear.txt)

### Inferences
- **Safe-to-block domains.** Blocking these does not affect routing or internet access:
  - Netgear: `*.ngxcld.com` (registration, presence, advisor) and the `peer*.netgear.com` endpoints (the latter serve app/remote features)
  - TP-Link: `tplinkdns.com`, `tplinklogin.net`
  - UniFi: `trace.svc.ui.com`
- **Blocking removes a feature:**
  - `tplinkcloud.com` and `genieremote.netgear.com`: remote/app access
  - `readycloud`/`readyshare`: USB cloud sharing
  - `*.ui.com` beyond trace: cloud console access and updates
- **Keep reachable (or allow periodically):**
  - Firmware update hosts: `updates1/2/3.netgear.com` and ASUS/TP-Link update hosts
  - The vendor's connectivity-check host (`www.netgear.com`, `www.tp-link.com`)

  Blocking the connectivity check can make the router report "no internet" or retry constantly, which is the high query counts seen in the Netgear and TP-Link reports.
- **Security add-ons are the biggest exposure.** Trend Micro and Bitdefender see per-URL or per-domain lookups for all LAN traffic. Plain telemetry is device-level stats. For privacy, turning off AiProtection or Armor matters more than DNS-blocking telemetry hosts.

### Gaps
- No sourced domain list was found for ASUS (firmware check, `dlcdnets.asus.com`, `asusrouter.com` DDNS, Trend Micro backends), Linksys/Velop, eero (beyond `eero.com`), Google Nest Wifi, MikroTik (IP → Cloud DDNS, update server) or Synology SRM.
  - MikroTik and Synology were not researched within the tool budget.
  - SNBForums returned 403.
- ISP-specific details were not researched per carrier: which carriers allow TR-069 to be disabled, and each carrier's bridge/passthrough procedure (Xfinity bridge mode, AT&T BGW IP Passthrough, Verizon Fios, Spectrum, BT Hub, Sky, Virgin modem mode).
- The HomeShield/Avira data flows on TP-Link were not confirmed from a primary source.
- `devicelocation.ngxcld.com` and `nw-dlcdnet.asus.com`'s exact roles are unverified.
- The status of the TP-Link federal ban after mid-2026 is unconfirmed.

## 2. Caveat: DNS blocking only works if the router's own lookups go through Pi-hole

### Takeaway
Pi-hole only sees a router's queries if the router's own WAN DNS points to Pi-hole. Handing out Pi-hole via DHCP to clients is not enough. Even then, hardcoded resolvers, DoH/DoT and direct-IP connections bypass it. TR-069 traffic on ISP gateways is out of reach entirely.

### Cited Findings
- **Encrypted DNS bypass:** Devices with encrypted DNS (DoH) send queries straight to Google/Cloudflare over HTTPS. Pi-hole never sees them, so they are neither blocked nor logged. XDA observed IoT gadgets reaching telemetry servers that were blocked in Pi-hole — [XDA: smart home bypassing Pi-hole with encrypted DNS](https://www.xda-developers.com/smart-home-gadgets-ignoring-pi-hole-encrypted-dns/)
- **Routers resist a LAN resolver:**
  - Several Pi-hole forum threads show routers (Netgear, Linksys) that won't accept or hand out a LAN resolver, or behave oddly when their own DNS is Pi-hole.
  - The documented workaround for Netgear routers is to set WAN DNS to Pi-hole. This routes the router's own lookups (e.g., updates1.netgear.com) through Pi-hole, where they then show up.

  — [Pi-hole Discourse: NetGear router does not like local DNS](https://discourse.pi-hole.net/t/netgear-router-does-not-like-local-dns/28897); [Linksys router won't designate Pi-hole](https://discourse.pi-hole.net/t/linksys-router-wont-designate-pi-hole-as-dns/55276); [TP-Link FAQ: using Pi-hole DNS on TP-Link routers](https://www.tp-link.com/us/support/faq/3230/)
- **Hosts-file sinkhole:** Custom-firmware users edit the router's own hosts file to sinkhole `registration.ngxcld.com`, because the binary embeds the URL — [SNBForums R7800 custom firmware thread (via search summary)](https://www.snbforums.com/threads/custom-firmware-build-for-r7800-v-1-0-2-67sf-1-0-2-67-1sf.56921/page-4)
- **DNS-over-TLS on ASUS:** ASUS routers support DoT upstream. If it is enabled on the router, its own and forwarded lookups bypass a Pi-hole placed upstream of it. This is an inference from the feature's existence — [ASUS FAQ: DNS over TLS](https://www.asus.com/support/faq/1051428/)

### Inferences
- **Two cases:**
  - Router is the DHCP/DNS server and forwards to Pi-hole: Pi-hole sees the router's own lookups but every client appears as the router.
  - Pi-hole is handed out via DHCP but the router's WAN DNS is the ISP: Pi-hole sees clients but never the router's telemetry.
- **Verifying what the router contacts, in order of reliability:**
  1. Capture upstream of the router: a managed switch with port mirroring between the router WAN and the modem, or a transparent bridge/firewall (e.g., OPNsense in bridge mode) running tcpdump/Wireshark. Look at SNI in TLS ClientHello, DNS on 53/853, and flows to vendor IP ranges.
  2. The router's own system/DNS logs, if it has them (OpenWrt logread, Asuswrt-Merlin syslog).
  3. Pi-hole query log filtered to the router's client IP, which only works if the router's WAN DNS is Pi-hole.
- **Stopping hardcoded or encrypted DNS** requires firewall rules on a device you control: redirect outbound port 53, block 853, and block known DoH endpoints. On a consumer router you can't control its own egress. You can only filter it from a device placed upstream.

### Gaps
- I found no published packet-capture study listing hardcoded resolver IPs per router vendor.
- None of the retrieved sources gives a step-by-step port-mirroring guide for home users.

## 3. Mitigations: settings, DNS blocking, bridge mode, firmware replacement

### Takeaway
The steps below are ordered from least to most effort:
1. Turn off vendor toggles: analytics, security add-ons, remote/cloud management, UPnP.
2. DNS-block known telemetry hosts, but keep firmware-update and connectivity-check hosts reachable.
3. Put the ISP gateway in bridge/passthrough mode behind your own router.
4. Replace the firmware (OpenWrt, DD-WRT, FreshTomato, Asuswrt-Merlin) or use pfSense/OPNsense.

Cloud-mandatory systems (eero, Google Nest Wifi) can only be "fixed" by replacing them.

### Cited Findings
- **Netgear:**
  - Disable Router Analytics Data Collection (Advanced → Administration → Router Update) — [Pi-hole Discourse](https://discourse.pi-hole.net/t/netgear-now-collects-router-analytics-data-here-are-the-steps-to-disable-it/3306)
  - EU/UK users can use Settings → Data Collection; US users email analyticspolicy@netgear.com — [NETGEAR KB](https://kb.netgear.com/000064225/I-live-in-the-European-Union-or-United-Kingdom-how-do-I-opt-out-of-NETGEAR-analytics-data-collection); [Analytics Data Policy](https://www.netgear.com/about/analyticsdatapolicy/)
  - Turn off Armor in the app (Settings → Security) — [NETGEAR Community](https://community.netgear.com/discussions/en-home-armor/how-do-i-turn-off-armorbitdefender-on-my-orbi-router/1733734/replies/1734652)
- **ASUS:**
  - Withdraw the Trend Micro agreement (Administration → Privacy). This loses AiProtection, QoS and the analyzers — [MBReviews](https://www.mbreviews.com/trend-micro-aiprotection-asus/)
  - Disable data sharing at Administration → Firmware Upgrade/Privacy. Critical security updates still auto-install — [ASUS Privacy Policy](https://www.asus.com/terms_of_use_notice_privacy_policy/privacy_policy/)
- **UniFi:**
  - Set Analytics & Improvements to Off.
  - On a self-hosted controller, set `system.analytics.enabled=false`.
  - Block `trace.svc.ui.com`.

  — [UniHosted](https://www.unihosted.com/blog/unifi-s-internet-history-checking-information-on-privacy-and-data-handling-by-unifi)
- **TP-Link:**
  - Omada/EAP firmware (since June 2022) can disable cloud connection.
  - DNS-block `tplinkcloud.com`/`tplinknbu.com`, allowlisting `n-device-api.tplinkcloud.com` and `security.iot.i.tplinknbu.com` if you use Tapo cameras.

  — [sappafrancesco TP-Link README](https://github.com/sappafrancesco/dns-blocklists/blob/main/vendors/tplink/README.md)
- **Google Nest Wifi:** Turn off "Cloud services" and "Wifi point stats" in Google Home → Wi-Fi → Privacy settings. The account-to-network link is still kept — [Google Help](https://support.google.com/googlehome/answer/6246642?hl=en)
- **eero:** There is no opt-out short of removing the product — [How-To Geek](https://www.howtogeek.com/eeros-silent-cloud-syncs-are-turning-your-router-into-yet-another-tracking-device/)
- **TR-069 generally:** Disable remote management wherever the device allows it. On ISP gear it usually can't be disabled — [Computerworld](https://www.computerworld.com/article/1525268/home-routers-supplied-by-isps-can-be-compromised-en-masse.html); [Wikipedia: TR-069](https://en.wikipedia.org/wiki/TR-069)
- **Pi-hole placement:** Set the router's WAN/primary DNS to Pi-hole so the router's own queries are filtered and logged — [TP-Link FAQ 3230](https://www.tp-link.com/us/support/faq/3230/)
- **Asuswrt-Merlin** documents DNS privacy (DoT) configuration. It is the common route for ASUS owners who want finer control — [Asuswrt-Merlin wiki: DNS Privacy](https://github.com/RMerl/asuswrt-merlin/wiki/DNS-Privacy/8fee90361b329ee33ff6af8eb8f318b3d87acc21)

### Inferences
- **General hardening checklist:**
  - Disable UPnP unless it is needed (e.g., for game consoles).
  - Disable remote/cloud admin and the vendor app binding, and use local web admin only.
  - Don't subscribe to Armor, HomeShield Pro or AiProtection if their URL-lookup privacy tradeoff is unacceptable.
  - Keep automatic firmware updates, or check manually on a schedule. Security patches matter more than update-check telemetry.
- **ISP gateways:**
  - Put the gateway in bridge/modem mode (or IP passthrough, e.g., AT&T BGW) and run your own router behind it. The ISP still manages the gateway via TR-069, but only sees the WAN side of your own router.
  - Where the ISP allows it, use your own modem or ONT-compatible device. Per-carrier details were not researched (see Gaps).
- **Firmware replacement:**
  - OpenWrt, DD-WRT and FreshTomato remove vendor cloud agents entirely. OpenWrt's own telemetry is minimal: an opt-in package-feed check and NTP to pool.ntp.org by default.
  - pfSense/OPNsense on separate hardware gives full egress control.
  - These points about the firmware projects are based on general knowledge. No source was fetched in this session, so the report writer should verify them or state them cautiously.
- **What must stay allowed:** NTP (vendors often use their own NTP hosts or pool.ntp.org), firmware-update hosts, and the vendor connectivity-check host. Blocking the latter causes retry storms.

### Gaps
- No primary source was fetched for OpenWrt, DD-WRT or FreshTomato default outbound connections, or for pfSense/OPNsense setup.
- Per-ISP bridge/passthrough steps and whether TR-069 can be disabled per carrier were not researched.
- TP-Link HomeShield/Avira privacy terms were not retrieved.
- MikroTik (IP → Cloud: DDNS, time-zone autodetect, backup) and Synology SRM (QuickConnect, Safe Access) were not covered.
