# OS-Level Controls That Complement DNS Blocking of Microsoft Telemetry (Windows 10/11, as of Sept 2026)

Scope note: Findings come from 20 search/fetch calls. Primary sources (learn.microsoft.com Policy CSP, the Windows privacy docs, the Microsoft 365 Apps privacy docs, the Edge policy reference, the O&O vendor blog) were preferred. Where only secondary or forum sources were found, that is stated. Registry paths are quoted from Microsoft docs unless noted otherwise.

## 1. Why DNS blocking alone is insufficient (hosts-file bypass, DoH, Defender, pinning)

### Takeaway
DNS/hosts blocking is a leaky single layer. Windows hard-codes some Microsoft names in `dnsapi.dll`, so the hosts file does not apply to them. Defender treats hosts entries for Microsoft telemetry domains as a "severe" threat and deletes them. Windows, Edge, Chrome and Firefox can each send DNS over HTTPS (DoH) to resolvers that skip a local Pi-hole. Telemetry uses TLS with certificate pinning, so its contents cannot be inspected. Microsoft also says some traffic, such as certificate revocation checks (CRL/OCSP), cannot be turned off at all. DNS blocking therefore has to be combined with policy/registry settings, service and task changes, and network enforcement (forced DNS plus an outbound firewall).

### Cited Findings
**Hosts file ignored for hard-coded Microsoft domains**
- Windows hard-codes a list of Microsoft domains in `%WINDIR%\system32\dnsapi.dll`, and the hosts file does not apply to them. The list includes microsoft.com, www.microsoft.com, windowsupdate.microsoft.com, update.microsoft.com, support.microsoft.com, office.microsoft.com, msdn.com and go.microsoft.com (17 domains in total). The behavior was "added… in Windows XP SP2, and it's still here in Windows 10". Petri gives Microsoft's rationale as stopping malware from overriding name resolution for the update servers. The article dates from 2016 and was updated September 2024. — [Petri](https://petri.com/windows-10-ignoring-hosts-file-specific-name-resolution/)
- Community reports say stopping the DNS Client (Dnscache) or Windows Update services does not stop the bypass. They name third-party DNS drivers such as YogaDNS as a workaround. These are forum claims, not verified. — [HardForum thread](https://hardforum.com/threads/how-to-edit-dnsapi-dll-in-windows-10-to-remove-hard-coded-telemetry-domains.2012159/); history dates back to 2006: [Slashdot 2006](https://slashdot.org/story/06/04/16/1351217/microsoft-bypasses-hosts-file), [MSFN XP SP2](https://msfn.org/board/topic/138261-modifying-dnsapidll-in-xp-sp2-for-ms-domains-in-hosts-file/)

**Microsoft Defender flags telemetry hosts entries**
- Since late July 2020, Defender has flagged hosts files that redirect Microsoft telemetry domains as **`SettingsModifier:Win32/HostsFileHijack`** (severity "Severe"). Domains that trigger it include `telemetry.microsoft.com`, `watson.telemetry.microsoft.com`, the vortex data servers and `wns.notify.windows.com.akadns.net`. Users can choose "Allow" on the detection, but Microsoft warned that doing so may also allow future malicious hosts changes. — [BleepingComputer](https://www.bleepingcomputer.com/news/microsoft/windows-10-hosts-file-blocking-telemetry-is-now-flagged-as-a-risk/)
- Microsoft's threat description says Defender "blocks any attempt to modify the hosts file to insert entries for specific, protected domains". When it remediates, it **resets the hosts file to default and removes all existing entries**, not only the Microsoft ones. — [Microsoft Security Intelligence (WDSI) entry](https://www.microsoft.com/en-us/wdsi/threats/malware-encyclopedia-description?name=SettingsModifier%3AWin32%2FHostsFileHijack&threatid=265754) (summary via search snippet); a variant name, `SettingsModifier:Win32/PossibleHostsFileHijack`, also exists — [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/3816415/settingsmodifier-win32-possiblehostsfilehijack)
- Spybot Anti-Beacon, which works by editing the hosts file, was a typical trigger. — [Samantha Johnson blog](https://www.samanthajohnson.co.uk/?p=2163); [Born's Tech](https://borncity.com/win/2020/08/03/windows-defender-lscht-windows-hosts-datei-teil-2/)

**DNS over HTTPS (DoH) at the OS and browser level**
- The Windows DNS client supports DoH, but only upgrades to it automatically when the configured DNS server is on a built-in **"known DoH servers"** list. The default list covers Cloudflare (1.1.1.1, 1.0.0.1), Google (8.8.8.8, 8.8.4.4) and Quad9 (9.9.9.9, 149.112.112.112), plus their IPv6 addresses. You can view the list with `Get-DnsClientDohServerAddress` and extend it with `Add-DnsClientDohServerAddress ... -AutoUpgrade $True`. The per-adapter choices are "Encrypted only", "Encrypted preferred, unencrypted allowed" and "Unencrypted only". — [Microsoft Learn: DoH client support](https://learn.microsoft.com/en-us/windows-server/networking/dns/doh-client-support)
- Group Policy: `Computer Configuration\Administrative Templates\Network\DNS Client\Configure DNS over HTTPS (DoH) name resolution` = **Allow / Prohibit / Require DoH**. **"Prohibit DoH"** is the OS-level switch that keeps Windows' own resolver on plain DNS to your Pi-hole. — [Microsoft Learn: DoH client support](https://learn.microsoft.com/en-us/windows-server/networking/dns/doh-client-support)
- The older registry toggle is `HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters\EnableAutoDoh` (DWORD 2 = enable). — [How-To Geek](https://www.howtogeek.com/765940/how-to-enable-dns-over-https-on-windows-11/); [Winaero](https://winaero.com/enable-dns-over-https-in-windows-11-also-known-as-doh/)
- Edge policy **`DnsOverHttpsMode`** takes `off` / `automatic` / `secure`, and **`BuiltInDnsClientEnabled`** controls Edge's own DNS client. Edge policies live under `HKLM\Software\Policies\Microsoft\Edge` (machine) or `HKCU\...` (user). — [Microsoft Edge policy reference](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies)
- Pi-hole answers the Firefox canary domain **`use-application-dns.net`** to tell Firefox that the network does not support DoH. Pi-hole community members stress that you must still block known DoH resolvers and block devices from reaching any resolver other than the internal one. — [Pi-hole Discourse: Blocking DoH](https://discourse.pi-hole.net/t/blocking-dns-over-https-doh/21359); [Pi-hole Discourse 2024 thread](https://discourse.pi-hole.net/t/blocking-dns-over-https-doh/69404)
- Community-maintained blocklists of DoH servers exist, some with 500+ domains. — [Pi-hole Discourse DoH blocklist how-to](https://discourse.pi-hole.net/t/dns-over-https-doh-blocklist/73182); [ckuethe DoH blocklist gist](https://gist.github.com/ckuethe/f71185f604be9cde370e702aa179fc2e)
- DoT uses TCP 853. DoH runs over 443, so blocking a port cannot stop it; only resolver-destination blocking can. — [Pi-hole Discourse DoH/DoT bypass](https://discourse.pi-hole.net/t/doh-dot-bypass-pi-hole/80956)

**Encrypted, pinned, and non-disableable traffic**
- "All diagnostic data is encrypted using TLS and uses **certificate pinning** during transfer." — [Microsoft Learn: Configure Windows diagnostic data](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- Documented diagnostic endpoints:
  - Connected User Experiences and Telemetry (DiagTrack): `v10.events.data.microsoft.com`, `v10c.events.data.microsoft.com`, `v10.vortex-win.data.microsoft.com`
  - Windows Error Reporting: `watson.telemetry.microsoft.com`, `umwatsonc.events.data.microsoft.com`, `*-umwatsonc.events.data.microsoft.com`, `*watcab0*.blob.core.windows.net`
  - Online Crash Analysis: `oca.telemetry.microsoft.com`, `kmwatsonc.events.data.microsoft.com`
  - Settings: `settings-win.data.microsoft.com`. Microsoft says "Don't block". It is used to remotely configure data collection and does not upload diagnostic data.
  - Authentication: `login.live.com` ("We don't recommend disabling"). — [same doc](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- Some telemetry uploads go to shared Azure blob storage (`*.blob.core.windows.net`), where blocking would also break unrelated services. — [same doc](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- "CRL and OCSP network traffic cannot be disabled and will still show up in network traces." — [Microsoft Learn: Manage connections from Windows OS components](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services)
- Microsoft's Restricted Traffic Baseline doc warns that "during Windows update/upgrade, egress traffic may occur". After "Reset this PC" the baseline must be re-applied, and traffic may flow before that happens. Microsoft recommends applying the baseline offline. — [same doc](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services)

**Hard-coded IPs**
- The hosts-bypass sources say the IPs behind Microsoft domains change often, so static IP blocking is unreliable. — [HardForum thread](https://hardforum.com/threads/how-to-edit-dnsapi-dll-in-windows-10-to-remove-hard-coded-telemetry-domains.2012159/)

### Inferences
- Blocking only through the hosts file is the weakest option on Windows: Defender wipes it, and `dnsapi.dll` overrides it for key domains. Blocking at a network DNS resolver (Pi-hole/AdGuard Home) avoids both problems. It still needs (a) DoH prohibited via GPO and browser policy, (b) port 53 forced/redirected at the router, (c) TCP/UDP 853 blocked, and (d) known DoH resolver IPs and domains blocked.
- Blocking `settings-win.data.microsoft.com` and `login.live.com` is likely to break things. Microsoft labels both as "don't block". This matters for anyone building an aggressive blocklist.
- Certificate pinning means TLS interception (mitmproxy) cannot inspect telemetry payloads. Verification has to rely on connection metadata (DNS logs, firewall logs, Wireshark SNI), or on Microsoft's Diagnostic Data Viewer on the device.

### Gaps
- I found no primary 2025–2026 source listing which domains `dnsapi.dll` currently hard-codes on Windows 11 24H2/25H2. The Petri list is from Windows 10. It is unconfirmed whether the list still exists on Windows 11.
- I found no reliable, current source showing that specific Windows telemetry components connect to **hard-coded IP literals** with no DNS lookup. The claim circulates, but I could not verify it.
- The Mozilla KB page on the `use-application-dns.net` canary failed to load. The specific rule (an NXDOMAIN/NODATA answer disables automatic DoH; DoH the user enabled themselves or DoH set by enterprise policy overrides the canary) comes from memory, not a source fetched in this session.
- Chrome's equivalent policy (`DnsOverHttpsMode` in Chrome) was not fetched. It is assumed to mirror Edge because both are Chromium.

## 2. Group Policy / registry controls (with edition requirements)

### Takeaway
Policy keys under `HKLM\SOFTWARE\Policies\...` are the most durable and supported way to reduce telemetry. However, **`AllowTelemetry=0` ("Diagnostic data off") only takes effect on Enterprise, Education, Server (and IoT Enterprise)**. On Home and Pro the effective floor is **Required (1)**. Many newer AI and Recall controls are Pro+ or Enterprise/Education only. Office, Edge, and developer tools (VS Code, .NET, PowerShell) have their own separate telemetry controls.

### Cited Findings
**Windows diagnostic data**
- `Computer Configuration > Administrative Templates > Windows Components > Data Collection and Preview Builds > Allow diagnostic data` sets registry value `HKLM\Software\Policies\Microsoft\Windows\DataCollection\AllowTelemetry` (DWORD). Values: 0 = Diagnostic data off (Security), 1 = Required, 2 = Enhanced (Windows 10 1809 and earlier only), 3 = Optional. — [Microsoft Learn: Configure Windows diagnostic data](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization); registry path from [Manage connections doc](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services)
- "Diagnostic data off… This is **only available on Windows Server, Windows Enterprise, and Windows Education editions**." Required is the default from Windows 10 1903 onward. — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- At the Off setting, "no Windows diagnostic data is sent". Microsoft's caveat: "no Windows Update information is collected when diagnostic data is off", and it recommends at least Required when relying on Windows Update. — [same](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- Required data includes: device, network, storage and processor attributes, including the **IMEI number**; lists of installed apps for compatibility; connected accessories; driver data; and Store usage. — [same](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- Optional data includes "browsing history and search terms" in Microsoft browsers, app launch and usage data, and crash memory dumps that may contain user content. — [same](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- Additional policies in the same folder: **Limit dump collection** and **Limit diagnostic log collection** (CSP `System/LimitDumpCollection`, `System/LimitDiagnosticLogCollection`; Windows 11 only), and **Configure diagnostic data opt-in settings user interface**, which stops users from raising the level. When both a computer and a user policy are set, the more restrictive one wins. — [same](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- Microsoft states explicitly that these settings cover only Windows OS components. "Third-party apps and other Microsoft apps, such as Microsoft 365 Apps… may also collect and send diagnostic data using their own controls." — [same](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- From March 6, 2024, **Edge diagnostic data in the EEA is collected separately** from Windows diagnostic data and has its own settings. — [same](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)

**Other Windows policies** (all from [Manage connections from Windows OS components](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services))
| Control | GPO | Registry (DWORD) |
|---|---|---|
| Advertising ID | Computer > Admin Templates > System > User Profiles > Turn off the advertising ID | `HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo\DisabledByGroupPolicy=1`; also `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo\Enabled=0` |
| Tailored experiences | User > ... > Cloud Content > Do not use diagnostic data for tailored experiences | `HKCU\SOFTWARE\Policies\Microsoft\Windows\CloudContent\DisableTailoredExperiencesWithDiagnosticData=1` |
| Consumer features (auto-installed apps/promos) | Computer > ... > Cloud Content > Turn off Microsoft consumer experiences | `HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent\DisableWindowsConsumerFeatures=1` |
| Spotlight | Cloud Content > Turn off all Windows Spotlight features | `...\CloudContent\DisableWindowsSpotlightFeatures=1` |
| Activity history | System > OS Policies: Enables Activity Feed / Allow publishing / Allow upload of User Activities | `HKLM\Software\Policies\Microsoft\Windows\System\EnableActivityFeed=0`, `PublishUserActivities=0`, `UploadUserActivities=0` |
| Cortana / web search | Windows Components > Search: Allow Cortana (off), Allow search and Cortana to use location (off), Do not allow web search (on), Don't search the web or display web results in Search (on) | `HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search\AllowCortana=0`, `AllowSearchToUseLocation=0`, `DisableWebSearch=1`, `ConnectedSearchUseWeb=0` |
| Windows Error Reporting | Windows Components > Windows Error Reporting > Disable Windows Error Reporting | `HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Error Reporting\Disabled=1` |
| CEIP | System > Internet Communication Management > Internet Communication Settings > Turn off CEIP | `HKLM\SOFTWARE\Policies\Microsoft\SQMClient\Windows\CEIPEnabled=0` |
| Delivery Optimization (no peer upload) | Delivery Optimization > Download Mode | `HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization\DODownloadMode=1` (HTTP only; per Microsoft doc) |
| OneDrive | OneDrive > Prevent the usage of OneDrive for file storage; Prevent OneDrive from generating network traffic until the user signs in | `HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive\DisableFileSyncNGSC=1`; `HKLM\SOFTWARE\Microsoft\OneDrive\PreventNetworkTrafficPreUserSignIn=1` |
| SmartScreen | Windows Components > Windows Defender SmartScreen > Configure Windows Defender SmartScreen = off | (security trade-off) |

- The Manage-connections doc warns against disabling **Windows Update, Automatic Root Certificates Update, and Microsoft Defender Antivirus**. It also warns that disabling the Microsoft Account Sign-In Assistant means "Windows Update will no longer offer feature updates" on Windows 10 1709+ and Windows 11. Disabling Teredo breaks some Xbox features and Delivery Optimization peering. The doc lists its applicability as Windows 11 Enterprise, Windows 10 Enterprise 1607+ and Server 2016/2019. — [same](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services)
- Microsoft ships the **Windows Restricted Traffic Limited Functionality Baseline** (`WindowsRTLFB.zip`), a Group Policy package. Once it is applied, the "Get Help" and "Give us feedback" links stop working. — [same](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services)

**Copilot / Recall / AI (Policy CSP "WindowsAI", ADMX `WindowsCopilot.admx`; doc updated 2026-09-23)** — [Microsoft Learn: WindowsAI Policy CSP](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-windowsai)
- **`AllowRecallEnablement`** (GPO "Allow Recall to be enabled", Computer > Windows Components > Windows AI; `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI\AllowRecallEnablement=0`). Setting it to disabled removes the Recall bits and deletes existing snapshots; a restart is required. Applies to **Pro, Enterprise and Education** on Windows 11 24H2 with KB5055627 (26100.3915) or later.
- **`DisableAIDataAnalysis`** (GPO "Turn off saving snapshots for use with Recall", computer and user scope; value 1 = no snapshots, and existing snapshots are deleted). Applies to Pro, Enterprise and Education on 24H2 with KB5055627 or later.
- **`DisableClickToDo`** (value 1). Pro, Enterprise and Education; the table lists Insider Preview.
- **`TurnOffWindowsCopilot`** (User > Windows Components > Windows Copilot; `HKCU\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot\TurnOffWindowsCopilot=1`). **Marked deprecated.** Microsoft notes it "isn't for the new Copilot experience", which is the Store-style Copilot app.
- **`RemoveMicrosoftCopilotApp`** uninstalls the Copilot app only if all of these hold: M365 Copilot is also installed, the user did not install the Copilot app, and it has not been launched in 28 days. Its table lists Enterprise and Education, while its text says "Enterprise, Professional and Education". Users can reinstall the app.
- **`SetCopilotHardwareKey`** remaps the Copilot key (Pro and up).
- **`DisableCocreator`**, **`DisableGenerativeFill`**, **`DisableImageCreator`** turn off Paint AI features: `HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Paint\...=1`.
- **`DisableSettingsAgent`** turns off agentic search in Settings (Enterprise and Education, Insider).
- Several AI policies (Recall deny lists, storage limits, agent connectors) are **Enterprise/Education only**.

**Office / Microsoft 365 Apps** — [Microsoft Learn: Manage privacy controls for M365 Apps](https://learn.microsoft.com/en-us/microsoft-365-apps/privacy/manage-privacy-controls)
- GPO location: `User Configuration\Policies\Administrative Templates\Microsoft Office 2016\Privacy\Trust Center` (requires the Office ADMX).
- Registry: `HKCU\Software\Policies\Microsoft\office\16.0\common\privacy`:
  - `disconnectedstate` (all connected experiences)
  - `usercontentdisabled` (experiences that analyze content)
  - `downloadcontentdisabled` (experiences that download online content)
  - `controllerconnectedservicesenabled` (optional connected experiences)
  - For all four: **1 = Enabled, 2 = Disabled**.
- `HKCU\Software\Policies\Microsoft\office\common\clienttelemetry\sendtelemetry`: **1 = Required, 2 = Optional, 3 = Neither**.
- Even with "Neither", "required service data will be sent". Disabling all connected experiences turns off co-authoring, online file storage and **Copilot features**. Licensing and other essential services keep working. The policies also apply to Microsoft 365 Apps for business.

**Edge** — [Edge policy reference](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies)
- Relevant policies: `DiagnosticData`, `PersonalizationReportingEnabled`, `EdgeShoppingAssistantEnabled`, `SpotlightExperiencesAndRecommendationsEnabled`, `HubsSidebarEnabled`, `CopilotPageContext` / `EdgeEntraCopilotPageContext`, `AlternateErrorPagesEnabled`, `NewTabPageContentEnabled`, `ConfigureDoNotTrack`, `DnsOverHttpsMode`.
- `EdgeFollowEnabled` is obsolete. `PromotionalTabsEnabled` and `WebWidgetAllowed` are listed as deprecated.

**Developer tools**
- .NET SDK/CLI telemetry is on by default. Opt out with `DOTNET_CLI_TELEMETRY_OPTOUT=1` (or `true`). — [Microsoft Learn: .NET CLI telemetry](https://learn.microsoft.com/en-us/dotnet/core/tools/telemetry)
- PowerShell 7 uses `POWERSHELL_TELEMETRY_OPTOUT`, and also needs `DOTNET_CLI_TELEMETRY_OPTOUT` for the underlying .NET. `TESTINGPLATFORM_TELEMETRY_OPTOUT` covers the MS Testing Platform. — [search summary of Microsoft Learn/.NET docs](https://learn.microsoft.com/en-us/dotnet/core/tools/telemetry); [NixOS issue discussing both vars](https://github.com/NixOS/nixpkgs/issues/74516)
- VS Code: `"telemetry.telemetryLevel": "off"` in settings.json. — (search summary; VS Code docs page not fetched)

### Inferences
- On Home and Pro, the realistic floor is `AllowTelemetry=1` plus disabling the DiagTrack service. Setting 0 in the registry on Pro is silently treated as 1, going by Microsoft's statement that Off is available only on Enterprise, Education and Server.
- Copilot controls are changing quickly. `TurnOffWindowsCopilot` is deprecated and does not cover the new app, so removing the Copilot app package and blocking reinstall is the practical approach on Home and Pro.
- Office telemetry is fully separate. A Windows-only hardening pass leaves it untouched.

### Gaps
- Registry names for `DisableSearchBoxSuggestions` (`HKCU\Software\Policies\Microsoft\Windows\Explorer`), `BingSearchEnabled` (`HKCU\...\Search`), `AllowNewsAndInterests` (Widgets: `HKLM\SOFTWARE\Policies\Microsoft\Dsh`), and Start menu recommendation policies (`HideRecommendedSection`, `HideRecommendedPersonalizedSites`) were **not verified against a Microsoft doc in this session**. They are widely cited but should be treated as unverified here.
- Current Edge `DiagnosticData` value semantics (0 = Off, 1 = Required, 2 = Optional) were not confirmed in the fetch output.
- I could not confirm the VS Code telemetry docs URL, or whether AI/Copilot extensions need separate settings.

## 3. Services and scheduled tasks (DiagTrack, dmwappushservice, Appraiser, CEIP), and whether updates re-enable them

### Takeaway
Microsoft's docs say the **Connected User Experiences and Telemetry** component (service name `DiagTrack`) handles diagnostic events and logs, and **Windows Error Reporting** handles crash data. Disabling DiagTrack is the main lever on Home and Pro, where `AllowTelemetry=0` is not honored. Scheduled tasks such as **Microsoft Compatibility Appraiser** (`\Microsoft\Windows\Application Experience\`, which runs CompatTelRunner.exe) collect independently. Community sources consistently report that feature updates reset services and tasks to their defaults, so the settings must be re-applied or enforced.

### Cited Findings
- Diagnostic events and logs are "managed by the Connected User Experiences and Telemetry component". Crash dumps go through Windows Error Reporting. — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- Microsoft Compatibility Appraiser lives at `Task Scheduler Library\Microsoft\Windows\Application Experience`. One Microsoft Q&A case found Compatibility Telemetry still running after a cumulative update, and the cause was this task, not the service. — [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/3987504/how-to-completely-and-permanently-disable-delete-w); [MakeUseOf](https://www.makeuseof.com/this-windows-process-comes-back-after-every-update-and-quietly-chews-through-your-files/)
- "Feature updates can reset privacy toggles and re-enable DiagTrack." Updates "lay down a fresh system layer", so tasks and services that were disabled are treated as unconfigured. Users report CompatTelRunner returning even after they replaced the executable. These are secondary and forum sources. — [WindowsForum](https://windowsforum.com/threads/disable-windows-11-telemetry-diagtrack-for-privacy-and-a-quieter-pc.400259/); [MakeUseOf](https://www.makeuseof.com/this-windows-process-comes-back-after-every-update-and-quietly-chews-through-your-files/)
- privacy.sexy recommends "regularly applying your configuration… especially after each new release and major operating system updates". — [privacy.sexy GitHub](https://github.com/undergroundwires/privacy.sexy)
- O&O ShutUp10 **Premium** "continuously monitors your selected settings and automatically restores them, even after Windows updates". — [rain-city.tech roundup](https://rain-city.tech/blog/best-windows-debloat/) (secondary; vendor page [O&O Premium](https://www.oo-software.com/en/ooshutup10premium/update))

### Inferences
- Policy-based settings (HKLM\SOFTWARE\Policies) generally survive cumulative updates better than service start types or disabled tasks, because Group Policy re-applies them. For services and tasks, a startup script or scheduled re-application (or ShutUp10 Premium or privacy.sexy re-runs) is the practical answer.
- Candidate tasks, commonly targeted by tools, **not verified against Microsoft docs here**:
  - `\Microsoft\Windows\Application Experience\ProgramDataUpdater`
  - `\Microsoft\Windows\Customer Experience Improvement Program\Consolidator`
  - `\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip`
  - `\Microsoft\Windows\Autochk\Proxy`
  - `\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector`
  - `\Microsoft\Windows\Feedback\Siuf\DmClient`

### Gaps
- There is no Microsoft primary doc on the role of `dmwappushservice` (WAP Push Message Routing Service, used by MDM) or on the side effects of disabling it. Disabling it may break Intune/MDM enrollment. That is an inference; no source was found.
- I found no Microsoft source confirming or denying that cumulative (as opposed to feature) updates re-enable DiagTrack.

## 4. Third-party tools: trustworthiness and maintenance in 2026

### Takeaway
**O&O ShutUp10++** (freeware from a German vendor; v2.x/3.x in 2025–2026, with Copilot and Recall controls) and **privacy.sexy** (open source, AGPL-3.0, v0.13.x, generates auditable and revertible scripts) are the most defensible choices. **Chris Titus WinUtil** (MIT, PowerShell, very popular) is broader and more aggressive. **WindowsSpyBlocker** exists, but I could not confirm that it is being maintained. The risk of aggressive debloaters is that they remove or disable components (Store, Defender, Update, Sign-In Assistant) that Microsoft itself warns against disabling.

### Cited Findings
- **O&O ShutUp10++**:
  - The vendor blog announces v2.0.1009 with Copilot removal, app uninstall (via O&O AppBuster) and Recall data deletion (via O&O SafeErase). — [O&O blog](https://blog.oo-software.com/en/new-oo-shutup10-2-0-1009-now-with-copilot-removal-app-uninstall-recall-data-deletion/); [Neowin](https://www.neowin.net/software/oo-shutup10-update-block-copilot--windows-recall/)
  - A later blog post covers v3.5.1130. — [O&O blog](https://blog.oo-software.com/en/new-oo-shutup10-version-3-5-1130-enhanced-speech-output-and-keyboard-navigation-more/)
  - The search summary described a v3.1.1104 dated 17/06/2026 and a move to .NET 8 as a single portable exe. **These version numbers conflict** (3.1.1104 vs 3.5.1130), so check the [changelog](https://www.oo-software.com/en/shutup10/changelog) for the current build.
  - The changelog notes reliable Secure Boot certificate status detection on 24H2/25H2 and a fix for the AI tab's Recall folder deletion error on Copilot+ PCs. — [O&O changelog](https://www.oo-software.com/en/shutup10/changelog) (via search summary)
- **privacy.sexy**: v0.13.8, AGPL-3.0. Supports Windows 10/11, macOS and Linux. It generates scripts, offers revert scripts, and has web and desktop versions. It is actively maintained. — [GitHub](https://github.com/undergroundwires/privacy.sexy)
- **WinUtil (Chris Titus)**: MIT license, 46,800+ GitHub stars, "30 million runs", pure PowerShell. It creates a restore point automatically and bundles app removal, telemetry tweaks, WinGet installs, Windows Update management and ISO creation. — [rain-city.tech](https://rain-city.tech/blog/best-windows-debloat/) (secondary blog; figures not independently verified)
- Reviewers call ShutUp10++ "more manual and transparent… easier to selectively apply changes" than WinUtil. — [rain-city.tech](https://rain-city.tech/blog/best-windows-debloat/); a comparison thread is at [ElevenForum](https://www.elevenforum.com/t/win11debloat-or-o-o-shutup10.27658/)
- **WindowsSpyBlocker** (crazy-max) is a Go single-binary tool with 845 commits. It builds its rules from captured traffic, and its docs are at crazymax.dev. The fetch could not confirm when it was last updated. — [GitHub](https://github.com/crazy-max/WindowsSpyBlocker)
- Microsoft's own warning about disabling Windows Update, root certificate updates, Defender and the MSA Sign-In Assistant covers the main risks of aggressive debloat. — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services)

### Inferences
- A good order of preference is:
  1. Native GPO/registry policies, including Microsoft's RTLFB baseline.
  2. ShutUp10++ using only its "recommended" (green) settings, or a reviewed privacy.sexy "Standard" script.
  3. WinUtil tweaks, selectively.
  4. Avoid unmaintained scripts (W10Privacy, older "Destroy Windows Spying"-style tools, Tron) on 24H2/25H2, where they can conflict with new components.
- Every tool should be run after a restore point, and re-run after feature updates.

### Gaps
- I did not verify the current maintenance status of WPD (Windows Privacy Dashboard), W10Privacy, Tron or Win11Debloat. None were researched in depth because of the tool-call budget.
- ShutUp10++'s exact "recommended settings" list was not fetched.
- I found no reputable security audit of WinUtil or privacy.sexy.

## 5. Network-level enforcement and verification; the "all privacy concerns" end-state (LTSC/Enterprise, accounts, BitLocker, OneDrive, Linux)

### Takeaway
Network enforcement means these layers together:
- a local resolver (Pi-hole/AdGuard Home)
- router NAT redirection of all port 53 traffic to that resolver
- blocking 853/DoT
- blocking known DoH endpoints
- ideally, per-app outbound firewall allowlisting

Verify with resolver query logs and packet capture, keeping in mind that Microsoft says CRL/OCSP and update-time traffic will still appear. For a real "Diagnostic data off", only **Enterprise, Education and IoT Enterprise (including LTSC)** qualify. A Microsoft account at setup now triggers automatic device encryption, with the **BitLocker recovery key backed up to the Microsoft account**, on all editions from 24H2, and Microsoft has been removing local-account workarounds in OOBE.

### Cited Findings
- Pi-hole users are told they "still need to block communications to any resolver from anything other than your intended internal DNS". — [Pi-hole Discourse](https://discourse.pi-hole.net/t/blocking-dns-over-https-doh/69404)
- CRL/OCSP traffic "cannot be disabled and will still show up in network traces". Microsoft recommends applying the restricted baseline offline and expects egress during updates. — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services)
- **Diagnostic data off** is limited to Server, Enterprise and Education. — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)
- The WindowsAI CSP tables list **IoT Enterprise / IoT Enterprise LTSC** as supported editions for the Recall and Copilot policies. — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-windowsai)
- Windows 11 IoT Enterprise LTSC 2024 has a 10-year support lifecycle, a frozen feature set, and quality and security updates only. It is intended for fixed-function devices. — [Microsoft Learn: What's new in Windows 11 IoT Enterprise LTSC 2024](https://learn.microsoft.com/en-us/windows/iot/iot-enterprise/whats-new/windows-11-iot-enterprise-ltsc-2024)
- In Windows 11 24H2, signing in with a Microsoft account during OOBE triggers automatic BitLocker device encryption on all editions, including Home. Recovery keys are backed up to the MSA, Entra ID or AD. With a local-only account, Home device encryption is unavailable and the keys are not stored online. — [ElcomSoft blog (May 2025)](https://blog.elcomsoft.com/2025/05/forensic-implications-of-bitlocker-by-default-in-windows-11-24h2/); [WindowsForum](https://windowsforum.com/threads/windows-11-oobe-now-account-first-local-account-bypass-removed-in-insider.383368/)
- Microsoft Insider leadership said: "We are removing known mechanisms for creating a local account in the Windows Setup experience (OOBE)." The BYPASSNRO workaround was removed. — [WindowsForum (Insider report)](https://windowsforum.com/threads/windows-11-oobe-now-account-first-local-account-bypass-removed-in-insider.383368/) (secondary; the source Insider blog post was not fetched)
- OneDrive can be blocked by policy with `DisableFileSyncNGSC=1` and `PreventNetworkTrafficPreUserSignIn=1`. — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/privacy/manage-connections-from-windows-operating-system-components-to-microsoft-services)
- Windows diagnostic data "processor configuration" (GDPR controller mode) requires an Entra-joined device on Pro, Enterprise or Education. In it, the organization becomes the controller, but data still flows to Microsoft. — [Microsoft Learn](https://learn.microsoft.com/en-us/windows/privacy/configure-windows-diagnostic-data-in-your-organization)

### Inferences
Prioritized practical stack, from highest to lowest leverage relative to breakage:
1. **Edition choice.** Enterprise/Education/IoT LTSC with `AllowTelemetry=0` is the only supported "off". On Home/Pro, accept Required and layer the steps below.
2. **Account.** Use a local account, or remove the MSA after setup. Check BitLocker key escrow in the Microsoft account's device list, and remove the key after saving it locally if desired. Turn off OneDrive Known Folder Move / backup.
3. **Policies.** Apply the policy table in section 2 plus the AI/Recall/Copilot and Office/Edge policies. These are low breakage apart from Search web results and Spotlight.
4. **Services and tasks.** Disable DiagTrack and the Appraiser/CEIP tasks, and re-apply after feature updates.
5. **Network.**
   - A Pi-hole/AdGuard blocklist, excluding `settings-win.data.microsoft.com`, `login.live.com` and Windows Update/CRL endpoints to avoid breakage.
   - Force DNS by redirecting 53, blocking 853, and blocking DoH resolvers.
   - Prohibit DoH via GPO and Edge/Chrome policy.
   - Optionally, an outbound Windows Firewall allowlist (for example with simplewall).
6. **Verify.** Check Pi-hole query logs for `*.events.data.microsoft.com` and `watson` after a reboot and an idle period. Use Wireshark SNI to catch DoH or direct-IP flows.
7. **Linux** for users who need no Microsoft traffic at all.

### Gaps
- **Windows 10 post-EOL (October 14, 2025) / ESU:** no sources were fetched on ESU enrollment requirements (for example, whether consumer ESU requires Microsoft account sign-in or Windows Backup sync) or on its privacy implications. This needs its own research.
- I found no authoritative, maintained list of Microsoft telemetry IP ranges suitable for firewall blocking. The WindowsSpyBlocker firewall lists exist, but I could not confirm when they were last updated.
- There is no primary source on simplewall's maintenance status in 2026.
- It is not confirmed whether the 24H2 OOBE local-account removal is in general-availability builds (25H2) or only in Insider builds. The source is a secondary forum report.
