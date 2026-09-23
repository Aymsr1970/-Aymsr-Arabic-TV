#!/usr/bin/env python3
from pathlib import Path
from urllib.request import Request, urlopen
import re
import time

OUTPUT = Path("Ayman-Arabic-TV-v2.m3u")

SOURCES = [
    ("Egypt", "https://iptv-org.github.io/iptv/countries/eg.m3u"),
    ("Arab World", "https://iptv-org.github.io/iptv/regions/arab.m3u"),
    ("Arabic Language", "https://iptv-org.github.io/iptv/languages/ara.m3u"),
    ("Free-TV Egypt", "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_egypt.m3u8"),
]

# Explicitly block Christian religious channels/streams while preserving Muslim religious channels.
BLOCK = [
    "aghapy", "coptic tv", "coptictv", "atvsat",
    "the kingdom sat", "thekingdomsat", "kingdomsat", "malakoot",
    "sat-7", "sat7", "al karma", "alkarma",
    "christian youth", "cycnow", "elbeshara",
    "al horreya", "alhorreya", "noursat",
    "nour al sharq", "nour el shabeb", "nour mariam", "nour al koddass",
    "logos tv", "miracle channel", "abn sat", "abnsat",
    "alhayat-live", "alhayattv.us",
]

CUSTOM = [
    # Egypt priority
    ('CBC','CBC.eg','🇪🇬 Egypt','https://flu.systemnet.tv/CBC/index.m3u8',None),
    ('CBC Drama','CBCDrama.eg','🇪🇬 Egypt','https://flu.systemnet.tv/CBCDrama/index.m3u8',None),
    ('CBC Sofra','CBCSofra.eg','🇪🇬 Egypt','https://flu.systemnet.tv/CBCSofra/index.m3u8',None),
    ('TEN TV','TenTV.eg','🇪🇬 Egypt','https://weyyak-live.akamaized.net/weyyak_ten_tv/index.m3u8',None),
    ('Al Qahera News','AlQaheraNews.eg','🇪🇬 Egypt','https://bcovlive-a.akamaihd.net/d30cbb3350af4cb7a6e05b9eb1bfd850/eu-west-1/6057955906001/playlist.m3u8',None),
    ('Al Ghad Plus','AlGhadPlus.eg','🇪🇬 Egypt','https://playlist.fasttvcdn.com/pl/ykvm3f2fhokwxqsurp9xcg/alghad-plus/playlist.m3u8',None),
    ('MBC Masr Drama','MBCMasrDrama.sa','🇪🇬 Egypt','https://shd-gcp-live.edgenextcdn.net/live/bitmovin-mbc-masr-drama/567b703c19ede6598222de81b0e4508b/index.m3u8',None),

    # Rotana
    ('Rotana Cinema KSA','RotanaCinemaKSA.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/cinema_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Rotana Cinema Egypt','RotanaCinemaEgypt.eg','📺 Rotana','https://rotana.hibridcdn.net/rotananet/cinemamasr_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Rotana Comedy','RotanaComedy.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/comedy_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Rotana Classic','RotanaClassic.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/classical_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Rotana Drama','RotanaDrama.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/drama_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Rotana Khalijia','RotanaKhalijia.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/khaleejiya_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Rotana Clip','RotanaClip.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/clip_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Rotana Music','RotanaMusic.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/music_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Al Resalah','AlResalah.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/risala_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('LBC (Rotana)','LBC.sa','📺 Rotana','https://rotana.hibridcdn.net/rotananet/lbc_net-7Y83PP5adWixDF93/playlist.m3u8','https://rotana.net/'),
    ('Rotana Kids','RotanaKids.sa','📺 Rotana','https://shls-rotanakids-prod-dub.shahid.net/out/v1/df6e0eb3cdc4410b98209aafc8677cef/index.m3u8',None),
    ('Rotana Aflam+','RotanaAflamPlus.sa','📺 Rotana','https://d35j504z0x2vu2.cloudfront.net/v1/master/0bc8e8376bd8417a1b6761138aa41c26c7309312/rotana-aflam-plus/master.m3u8',None),
]

COUNTRY_GROUP = {
    'eg':'🇪🇬 Egypt','sa':'🇸🇦 Saudi Arabia','ae':'🇦🇪 UAE','kw':'🇰🇼 Kuwait',
    'qa':'🇶🇦 Qatar','bh':'🇧🇭 Bahrain','om':'🇴🇲 Oman','jo':'🇯🇴 Jordan',
    'lb':'🇱🇧 Lebanon','ps':'🇵🇸 Palestine','iq':'🇮🇶 Iraq','sy':'🇸🇾 Syria',
    'ye':'🇾🇪 Yemen','sd':'🇸🇩 Sudan','ly':'🇱🇾 Libya','tn':'🇹🇳 Tunisia',
    'dz':'🇩🇿 Algeria','ma':'🇲🇦 Morocco','mr':'🇲🇷 Mauritania','so':'🇸🇴 Somalia',
    'dj':'🇩🇯 Djibouti','km':'🇰🇲 Comoros'
}

def fetch(url):
    req=Request(url, headers={'User-Agent':'Mozilla/5.0 Ayman-Arabic-TV-Builder/3.0'})
    last=None
    for _ in range(3):
        try:
            with urlopen(req, timeout=35) as r:
                return r.read().decode('utf-8','replace')
        except Exception as e:
            last=e
            time.sleep(2)
    print(f"WARNING: failed source {url}: {last}")
    return ""

def parse(text):
    lines=text.splitlines()
    out=[]
    i=0
    while i<len(lines):
        line=lines[i].strip()
        if line.startswith('#EXTINF'):
            meta=line
            aux=[]
            i+=1
            while i<len(lines) and lines[i].strip().startswith('#') and not lines[i].strip().startswith('#EXTINF'):
                aux.append(lines[i].strip())
                i+=1
            if i<len(lines):
                url=lines[i].strip()
                if url and not url.startswith('#'):
                    out.append({'meta':meta,'aux':aux,'url':url,'custom':False})
        i+=1
    return out

def get_name(meta):
    return meta.split(',',1)[1].strip() if ',' in meta else meta

def get_id(meta):
    m=re.search(r'tvg-id="([^"]*)"',meta,re.I)
    return m.group(1) if m else ''

def base_id(tvg):
    return tvg.split('@',1)[0].strip()

def normalize_name(name):
    name=re.sub(r'\[[^\]]+\]','',name)
    name=re.sub(r'\([^)]*(?:\d{3,4}p|HD|SD|FHD|4K)[^)]*\)','',name,flags=re.I)
    return re.sub(r'[^a-z0-9\u0600-\u06ff]+','',name.lower())

def blocked(e):
    s=(e['meta']+' '+' '.join(e['aux'])+' '+e['url']).lower()
    return any(x in s for x in BLOCK)

def valid_url(url):
    u=url.lower()
    return (u.startswith('http://') or u.startswith('https://')) and '.mpd' not in u

def group_for(e):
    name=get_name(e['meta'])
    if name.lower().startswith('rotana ') or name.lower().startswith('rotana+'):
        return '📺 Rotana'
    if name.lower().startswith('mbc ') or name.lower().startswith('mbc+'):
        # keep Egyptian MBC feeds in Egypt if their id/name says Masr
        if 'masr' in name.lower():
            return '🇪🇬 Egypt'
        return '📺 MBC'
    tvg=base_id(get_id(e['meta']))
    m=re.search(r'\.([a-z]{2})$',tvg,re.I)
    if m:
        cc=m.group(1).lower()
        if cc in COUNTRY_GROUP:
            return COUNTRY_GROUP[cc]
    return '🌍 Arabic International'

def set_group(meta,group):
    if re.search(r'group-title="[^"]*"',meta,re.I):
        return re.sub(r'group-title="[^"]*"',f'group-title="{group}"',meta,flags=re.I)
    comma=meta.find(',')
    if comma==-1:
        return meta
    return meta[:comma]+f' group-title="{group}"'+meta[comma:]

def score(e):
    s=0
    u=e['url'].lower()
    meta=e['meta'].lower()
    if e.get('custom'): s+=1000
    if u.startswith('https://'): s+=40
    if '.m3u8' in u: s+=30
    if '1080p' in meta: s+=8
    if '720p' in meta: s+=5
    if 'geo-blocked' in meta: s-=20
    if 'not 24/7' in meta: s-=5
    return s

entries=[]
for name,tvg,group,url,ref in CUSTOM:
    aux=[f'#EXTVLCOPT:http-referrer={ref}'] if ref else []
    entries.append({
        'meta':f'#EXTINF:-1 tvg-id="{tvg}" tvg-name="{name}" group-title="{group}",{name}',
        'aux':aux,'url':url,'custom':True
    })

for label,url in SOURCES:
    txt=fetch(url)
    if not txt:
        continue
    print(f"Fetched {label}")
    entries.extend(parse(txt))

# Filter, normalize groups, and keep the best stream for each channel identity.
best={}
for e in entries:
    if blocked(e) or not valid_url(e['url']):
        continue
    name=get_name(e['meta'])
    tvg=base_id(get_id(e['meta']))
    key=('id:'+tvg.lower()) if tvg else ('name:'+normalize_name(name))
    e['meta']=set_group(e['meta'],group_for(e))
    old=best.get(key)
    if old is None or score(e)>score(old):
        best[key]=e

group_order = {
    '🇪🇬 Egypt':0,'📺 Rotana':1,'📺 MBC':2,
    '🇸🇦 Saudi Arabia':3,'🇦🇪 UAE':4,'🇶🇦 Qatar':5,'🇰🇼 Kuwait':6,
    '🇧🇭 Bahrain':7,'🇴🇲 Oman':8,'🇯🇴 Jordan':9,'🇱🇧 Lebanon':10,
    '🇵🇸 Palestine':11,'🇮🇶 Iraq':12,'🇸🇾 Syria':13,'🇾🇪 Yemen':14,
    '🇸🇩 Sudan':15,'🇱🇾 Libya':16,'🇹🇳 Tunisia':17,'🇩🇿 Algeria':18,
    '🇲🇦 Morocco':19,'🇲🇷 Mauritania':20,'🇸🇴 Somalia':21,'🇩🇯 Djibouti':22,
    '🇰🇲 Comoros':23,'🌍 Arabic International':30
}

def extract_group(meta):
    m=re.search(r'group-title="([^"]*)"',meta,re.I)
    return m.group(1) if m else '🌍 Arabic International'

result=list(best.values())
result.sort(key=lambda e:(group_order.get(extract_group(e['meta']),29), get_name(e['meta']).lower()))

lines=[
    '#EXTM3U',
    '# Ayman Arabic TV v3 AUTO',
    '# Sources: IPTV-org Egypt + Arab World + Arabic language + Free-TV Egypt',
    '# Christian religious channels filtered out; Islamic religious channels preserved.',
    '# Rotana group pinned from current public/officially referenced streams.',
]
for e in result:
    lines.append(e['meta'])
    lines.extend(e['aux'])
    lines.append(e['url'])

OUTPUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f"Wrote {OUTPUT} with {len(result)} channels")
