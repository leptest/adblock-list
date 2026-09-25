# Leptest's List

An Adblock Plus filter list that cleans up the leftovers on:

- https://paileactivist.github.io/toolz/adblock.html
- https://superadblocktest.com/
- https://obfusgated.com/tools/ad-block-test

Plus a set of Microsoft telemetry lists built for Pi-hole.

## Lists

| File | What it does | Add in Pi-hole as |
|------|--------------|-------------------|
| [`list.txt`](list.txt) | Ad networks, big-tech ads, vendor telemetry (see below) | Blocklist |
| [`microsoft.txt`](microsoft.txt) | Windows / Office / Edge / Xbox / dev-tool telemetry, Bing & MSN ads, Clarity. Does **not** break Windows Update, activation, Store, sign-in, OneDrive, Outlook, Teams, Defender or SmartScreen | Blocklist |
| [`microsoft-aggressive.txt`](microsoft-aggressive.txt) | Opt-in extras. Each section names what it breaks: Widgets and the Edge news feed, location, Timeline, feature experiments, Application Insights, Copilot | Blocklist (optional) |
| [`microsoft-allowlist.txt`](microsoft-allowlist.txt) | Microsoft hosts that must keep resolving, so other broad lists can't break updates, activation, sign-in, the "No internet" check or Defender | **Allowlist** |

## Subscribe

Raw URLs:

```
https://raw.githubusercontent.com/leptest/adblock-list/master/list.txt
https://raw.githubusercontent.com/leptest/adblock-list/master/microsoft.txt
https://raw.githubusercontent.com/leptest/adblock-list/master/microsoft-aggressive.txt
https://raw.githubusercontent.com/leptest/adblock-list/master/microsoft-allowlist.txt
```

- **Pi-hole v6:** Lists → add each URL. Use "Add blocklist" for the block lists and "Add allowlist" for `microsoft-allowlist.txt`. Then run `pihole -g` (or Tools → Update Gravity).
- **uBlock Origin / Adblock Plus / AdGuard:** add as custom filter lists. The allowlist isn't needed in a browser.

### Pi-hole compatibility

Pi-hole only accepts Adblock-style lines of the exact form `||example.com^`. It blocks that domain **and all its subdomains**. Anything with a modifier, such as `||example.com^$important`, is thrown away as invalid, and so are cosmetic `##` rules. Pi-hole also ignores `@@` exception rules inside a *blocklist*, so allow rules have to live in a separate list added as an allowlist.

Check a list before pushing:

```
python3 scripts/check_pihole.py list.txt microsoft.txt microsoft-aggressive.txt microsoft-allowlist.txt
```

## What `list.txt` blocks

- **Ad networks:** Google (AdSense, DoubleClick), Microsoft/AppNexus (adnxs), Fastclick, MGID, JW Player
- **Big tech ads & tracking:** Amazon, Facebook, Twitter, Pinterest, Reddit, YouTube, TikTok, Yahoo
- **Vendor telemetry:** Xiaomi (MIUI/mistat), OnePlus, Samsung, Apple metrics
- **Analytics:** Hotjar
- **Site-specific:** Moxfield deck-page ads (browser only; Pi-hole can't do cosmetic rules)
- **Misc:** Greatis (crypto-related)

## Contributing

Open an issue or PR if you spot ads that slip through on the test sites above.
