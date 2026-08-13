#!/usr/bin/env python3
"""Create the modern multi-page Catford Print site from the public legacy pages."""
import html
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "site-audit-deps"))
from bs4 import BeautifulSoup

ROOT = "https://www.catfordprint.co.uk/"
OUT = Path(__file__).resolve().parent
PAGES = [
 "A3-Black-Leaflets.html","A3-Colour-Leaflets.html","A4-Bespoke-Booklets.html","A4-Black-Leaflets.html","A4-Colour-Booklets.html","A4-Colour-Leaflets.html","A4-Letterheads.html","A4-Super-Economy-Booklets.html","A5-Bespoke-Booklets.html","A5-Black-Leaflets.html","A5-Colour-Booklets.html","A5-Colour-Leaflets.html","A5-Super-Economy-Booklets.html","A6-Bespoke-Booklets.html","A6-Colour-Booklets.html","A6-Super-Economy-Booklets.html","NCR-Sets.html","banners.html","book-printing.html","book-quotation.html","booklet-printers.html","booklet-quotation.html","calendar-printing.html","catford_print_video.html","cd-dvd-cover-printing.html","cheap-leaflets.html","christmas-card-printing.html","funeral-order-of-service.html","hardback-book-printing-uk.html","index-March-2020.html","internet-printers.html","large-posters.html","leaflet-quotation.html","leaflets-uk.html","london-printers.html","menu-downloads.html","menu-environmental.html","ncrdesign.html","paperback-book-printing-uk.html","printed-business-cards.html","printing-fulfilment.html","printing-quotation.html","privacy.html","stationery.html","terms.html","vat-rules-for-printing.html","wire-o-binding.html"
]
NAV_WORDS={"Home","Books","Booklets","Posters","Outdoor Banners","Business Cards","Stationery","Funeral Service Templates","Leaflets","Wire-o Binding","Online Quote","Email Us","Contact Us","Upload Your File","Upload your file to our FTP site","How to find us"}

def fetch(name):
    req=Request(urljoin(ROOT,name),headers={"User-Agent":"Mozilla/5.0"})
    with urlopen(req,timeout=25) as response:
        return response.read().decode("utf-8","replace")

def clean_text(value):
    return re.sub(r"\s+"," ",value or "").strip()

def page_group(name):
    low=name.lower()
    if "booklet" in low: return "Booklet printing"
    if "leaflet" in low: return "Leaflet printing"
    if "book" in low: return "Book printing"
    if any(x in low for x in ("card","letterhead","ncr","stationery")): return "Business printing"
    if any(x in low for x in ("poster","banner","calendar","cd-dvd")): return "Display & specialist print"
    if any(x in low for x in ("privacy","terms","vat","environmental")): return "Information"
    return "Catford Print Centre"

def local_href(href):
    href=urldefrag(href)[0]
    parsed=urlparse(href)
    if parsed.netloc in ("www.catfordprint.co.uk","catfordprint.co.uk"):
        name=Path(parsed.path).name
        if name in PAGES or name=="index.html": return name
        if parsed.path.rstrip("/").endswith("sendfile"): return "https://www.catfordprint.co.uk/sendfile"
    return href

def extract_tables(soup):
    result=[]
    for table in soup.find_all("table"):
        if table.find("table"): continue
        rows=[]
        for tr in table.find_all("tr"):
            cells=[clean_text(c.get_text(" ",strip=True)) for c in tr.find_all(["th","td"],recursive=False)]
            if len(cells)>=2 and any(cells): rows.append(cells)
        if len(rows)>=2:
            signature="|".join("|".join(r) for r in rows)
            if len(signature)>30 and signature not in {x[0] for x in result}: result.append((signature,rows))
    return [rows for _,rows in result]

def extract_options(soup):
    fields=[]
    for i,select in enumerate(soup.find_all("select")):
        opts=[clean_text(o.get_text(" ",strip=True)) for o in select.find_all("option")]
        opts=[o for o in opts if o]
        if not opts: continue
        label=select.get("name") or select.get("id") or f"Option {i+1}"
        label=clean_text(label.replace("-"," ").replace("_"," ")).title()
        fields.append((label,opts))
    return fields

def embedded_form_fields(soup):
    fields=[]
    for frame in soup.find_all("iframe",src=True):
        src=urljoin(ROOT,frame["src"])
        if urlparse(src).netloc not in ("www.catfordprint.co.uk","catfordprint.co.uk"): continue
        try:
            embedded=BeautifulSoup(urlopen(Request(src,headers={"User-Agent":"Mozilla/5.0"}),timeout=20).read(),"html.parser")
        except Exception:
            continue
        for label,options in extract_options(embedded): fields.append((label,"select",options,""))
        used=set()
        for input_tag in embedded.find_all("input"):
            kind=(input_tag.get("type") or "text").lower(); name=input_tag.get("name") or ""
            if kind not in ("text","number") or not name or name in used or name in ("email","additional_100","additional_200","additional_300","additional_400"): continue
            used.add(name); label=clean_text(name.replace("_"," ").replace("-"," ")).title()
            fields.append((label,"number" if name in ("quantity","num_pages","num_inner_pages_in_black") else "text",[],input_tag.get("value") or ""))
    return fields

def embedded_calculators(soup):
    urls=[]
    for frame in soup.find_all("iframe",src=True):
        src=urljoin(ROOT,frame["src"])
        if urlparse(src).netloc in ("www.catfordprint.co.uk","catfordprint.co.uk") and "/ncr/" in urlparse(src).path:
            urls.append(src)
    return urls

def extract_lines(soup,title):
    for tag in soup(["script","style","noscript","iframe","svg"]): tag.decompose()
    lines=[]
    for value in soup.body.stripped_strings if soup.body else soup.stripped_strings:
        text=clean_text(value)
        if not text or text in NAV_WORDS or text==title: continue
        if text.startswith("javascript:"): continue
        if lines and text==lines[-1]: continue
        lines.append(text)
    return lines

def logo():
    return '''<a class="brand" href="index.html" aria-label="Catford Print Centre home"><svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true"><path d="M9 26 5 10l15 8A25 25 0 0 1 44 18l15-8-4 16a25 25 0 1 1-46 0Z" fill="currentColor"/><path d="M20 31c4-7 20-7 24 0-2 2-5 4-8 5l4 4-8 8-8-8 4-4c-3-1-6-3-8-5Z" fill="#fff"/></svg><span><strong>CATFORD</strong><small>PRINT CENTRE</small></span></a>'''

def shell(title,kicker,content,description=""):
    desc=description or f"{title} from Catford Print Centre."
    return f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{html.escape(desc[:155],quote=True)}"><title>{html.escape(title)} | Catford Print Centre</title><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@600;700;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="mobile-fixes.css"><link rel="stylesheet" href="page.css"><link rel="stylesheet" href="calculator.css"></head><body><a class="skip-link" href="#main">Skip to content</a><div class="announcement">Offices in Catford and New Addington, Croydon <span>•</span> Telephone hours: weekdays 9am–5pm</div><header class="site-header">{logo()}<button class="menu-toggle" aria-expanded="false" aria-controls="main-nav"><span></span><span></span><span></span><span class="sr-only">Menu</span></button><nav id="main-nav" class="main-nav" aria-label="Main navigation"><a href="all-services.html">All services</a><a href="printing-quotation.html">Online quote</a><a href="menu-downloads.html">Helpful guides</a><a href="internet-printers.html">Contact us</a><a class="nav-upload" href="https://www.catfordprint.co.uk/sendfile">Upload your file</a></nav></header><main id="main"><section class="page-hero"><div class="breadcrumbs"><a href="index.html">Home</a><span>/</span><span>{html.escape(kicker)}</span></div><p class="eyebrow">{html.escape(kicker)}</p><h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p></section>{content}</main><footer>{logo()}<p>Print &amp; Mail. Franking &amp; Posting Service.</p><div><a href="privacy.html">Privacy</a><a href="terms.html">Terms &amp; conditions</a></div><small class="page-footer-credit">© <span data-year></span> Catford Print Centre · Website made by <a href="https://beeseen.uk" target="_blank" rel="noopener noreferrer">BeeSeen.uk</a></small></footer><script src="site-pages.js"></script></body></html>'''

def create_page(name):
    raw=fetch(name); soup=BeautifulSoup(raw,"html.parser")
    title=clean_text(soup.title.get_text(" ",strip=True) if soup.title else Path(name).stem.replace("-"," ").title())
    if title in ("Untitled Document","Catford Print Centre"): title=Path(name).stem.replace("-"," ").replace("menu ","").title()
    tables=extract_tables(soup); options=extract_options(soup); embedded=embedded_form_fields(soup); calculators=embedded_calculators(soup); lines=extract_lines(soup,title)
    headings=[clean_text(h.get_text(" ",strip=True)) for h in soup.find_all(["h1","h2","h3"])]
    lead=next((x for x in lines if len(x)>55),f"Full details, options and ordering information for {title}.")
    copy=[]
    for line in lines:
        tag="h3" if (line in headings and len(line)<100) else "p"
        cls=' class="copy-line"' if tag=="p" else ""
        copy.append(f"<{tag}{cls}>{html.escape(line)}</{tag}>")
    option_html=""
    if options or embedded:
        fields=[]
        for i,(label,opts) in enumerate(options):
            fields.append(f'<label for="opt-{i}">{html.escape(label)}<select id="opt-{i}">'+''.join(f'<option>{html.escape(o)}</option>' for o in opts)+'</select></label>')
        offset=len(fields)
        for i,(label,kind,opts,value) in enumerate(embedded):
            field_id=f"embedded-{i+offset}"
            if kind=="select": control=f'<select id="{field_id}">'+''.join(f'<option>{html.escape(o)}</option>' for o in opts)+'</select>'
            else: control=f'<input id="{field_id}" type="{kind}" value="{html.escape(value,quote=True)}">'
            fields.append(f'<label for="{field_id}">{html.escape(label)}{control}</label>')
        option_html=f'<section class="content-section"><h2>Available options</h2><div class="option-panel"><div class="option-grid">{"".join(fields)}</div></div></section>'
    calculator_html=""
    if calculators:
        frames="".join(f'<iframe class="legacy-calculator" src="{html.escape(src,quote=True)}" title="{html.escape(title,quote=True)} live price calculator" loading="lazy"></iframe>' for src in calculators)
        calculator_html=f'<section class="content-section"><h2>Live price calculator</h2><p>Use the original Catford Print pricing engine for an instant price and any available spine estimate.</p><div class="calculator-frame">{frames}</div></section>'
    table_html=""
    if tables:
        rendered=[]
        for rows in tables:
            body=[]
            width=max(len(r) for r in rows)
            for row in rows:
                row=row+[""]*(width-len(row)); body.append("<tr>"+"".join(f"<td>{html.escape(cell)}</td>" for cell in row)+"</tr>")
            rendered.append('<div class="table-wrap"><table class="data-table">'+''.join(body)+'</table></div>')
        table_html=f'<section class="content-section"><h2>Prices, sizes and specifications</h2>{"".join(rendered)}</section>'
    content=f'''<div class="page-shell"><article class="page-content">{calculator_html}{option_html}<section class="content-section"><h2>Full details</h2><div class="legacy-copy">{"".join(copy)}</div></section>{table_html}</article><aside class="page-sidebar"><div class="sidebar-card"><h2>Ready to print?</h2><p>Send us your requirements for a firm price, or call for helpful advice.</p><a class="button primary" href="mailto:web@catfordprint.co.uk?subject={html.escape(title.replace(' ','%20'))}%20enquiry">Email us</a></div><div class="sidebar-card cyan"><h2>Send your artwork</h2><p>Upload files up to 50MB using our existing secure upload service.</p><a class="button ghost" href="https://www.catfordprint.co.uk/sendfile">Upload your file</a></div><div class="related-list"><h2>Explore the range</h2><a href="book-printing.html">Books <span>→</span></a><a href="booklet-printers.html">Booklets <span>→</span></a><a href="leaflets-uk.html">Leaflets <span>→</span></a><a href="stationery.html">Business print <span>→</span></a><a href="all-services.html">All services <span>→</span></a></div></aside></div>'''
    (OUT/name).write_text(shell(title,page_group(name),content,lead),encoding="utf-8")
    return title,lead

def create_directory(entries):
    cards=[]
    for name,title,lead in entries:
        if name=="index-March-2020.html": continue
        cards.append(f'<a class="directory-card" href="{html.escape(name)}"><b>{html.escape(title)}</b><span>{html.escape(page_group(name))} →</span></a>')
    content=f'<section class="service-directory"><div class="section-heading"><div><p class="eyebrow">Complete site directory</p><h2>Every product.<br><em>Every option.</em></h2></div><p>All services and information from the original Catford Print Centre website, rebuilt in the new style.</p></div><div class="directory-grid">{"".join(cards)}</div></section>'
    (OUT/"all-services.html").write_text(shell("All printing services","Complete range",content,"Browse every Catford Print Centre product, price, guide and service."),encoding="utf-8")

if __name__=="__main__":
    entries=[]
    for name in PAGES:
        try:
            title,lead=create_page(name); entries.append((name,title,lead)); print("created",name)
        except Exception as exc: print("ERROR",name,exc)
    create_directory(entries)
    print(f"Created {len(entries)} legacy pages plus the full service directory.")
