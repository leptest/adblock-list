# Port of pi-hole/FTL gravity-parseList.c line handling (ABP subset)
import re, sys
CH = re.compile(r'^[a-z0-9._-]+$')  # valid_domain_char is [A-Za-z0-9._-] ; lowercased first
def valid_domain(d):
    if not d or len(d) > 255 or not CH.match(d): return False
    labels = d.split('.')
    if any(len(l) == 0 or len(l) > 63 for l in labels): return False
    if labels[-1].startswith('-') or d.endswith('-'): return False
    return True
def check(path, allow):
    ok = bad = 0
    for raw in open(path):
        line = raw.rstrip()
        if not line or line[0] in '!#;[': continue
        if '##' in line or '#$#' in line or '#@#' in line or '#?#' in line or '#%#' in line: continue
        line = line.split('#')[0].strip().lower()
        pre = '@@||' if allow else '||'
        if line.startswith(pre) and line.endswith('^') and valid_domain(line[len(pre):-1]): ok += 1
        else: bad += 1; print('  INVALID:', line)
    print(f'{path}: {ok} accepted, {bad} invalid')
for p in sys.argv[1:]:
    check(p, 'allowlist' in p)
