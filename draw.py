#!/usr/bin/env python3
"""Render the 25 Nov 2026 front page as a 1024x1024 PNG.

Writes entry.png beside this file. Pillow is used only by this
drawing script; the submitted entrypoint (main.py) is stdlib-only.
"""
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(BASE, "entry.png")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 28
RIGHT = PAGE_W - MARGIN

CREAM = (248, 244, 235)
BLACK = (18, 18, 18)
GREY = (92, 86, 74)
CRIMSON = (176, 32, 26)
NAVY = (20, 22, 28)
HAIRLINE = (152, 144, 128)
CARD = (255, 255, 255)
EDGE = (206, 199, 183)
GOLD = (238, 198, 88)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_ITAL = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def fit_words(canvas, text, typeface, width):
    """Split text into lines no wider than width (greedy)."""
    out, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if canvas.textlength(trial, font=typeface) <= width:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def block_text(canvas, text, typeface, x, y, width, leading, colour=BLACK,
               max_lines=None):
    """Draw a wrapped block; return the y just below it."""
    lines = fit_words(canvas, text, typeface, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        canvas.text((x, y), line, font=typeface, fill=colour)
        y += leading
    return y


def shrink_line(canvas, text, path, size, width, floor=10):
    """Biggest size at or under `size` that fits `text` on one line."""
    s = size
    while s > floor:
        face = load(path, s)
        if canvas.textlength(text, font=face) <= width:
            return face
        s -= 1
    return load(path, floor)


def draw_diagram(canvas, left, top, right, bottom):
    """Hub-and-spoke sketch of the breached OSINT network.

    Rectangular tags around a crimson hub, joined by thin spokes.
    """
    canvas.rounded_rectangle([left, top, right, bottom], radius=10,
                             outline=EDGE, width=2, fill=CARD)
    hub_x, hub_y = (left + right) // 2, (top + bottom) // 2 + 4
    tag_face = load(SANS_BOLD, 13)
    tags = [
        ("CIA", hub_x - 118, hub_y - 62),
        ("ODNI", hub_x + 118, hub_y - 62),
        ("NGA", hub_x - 118, hub_y + 62),
        ("SATELLITE", hub_x + 118, hub_y + 62),
        ("SOCIAL MEDIA", hub_x, hub_y - 72),
    ]
    for label, tx, ty in tags:
        canvas.line([(hub_x, hub_y), (tx, ty)], fill=(125, 125, 125), width=2)
    for label, tx, ty in tags:
        tw = canvas.textlength(label, font=tag_face)
        pad = 11
        canvas.rounded_rectangle(
            [tx - tw / 2 - pad, ty - 15, tx + tw / 2 + pad, ty + 15],
            radius=7, outline=GREY, width=1, fill=(233, 229, 217))
        canvas.text((tx - tw / 2, ty - 9), label, font=tag_face, fill=BLACK)
    canvas.rounded_rectangle([hub_x - 72, hub_y - 28, hub_x + 72, hub_y + 28],
                             radius=12, fill=CRIMSON)
    hub_face = load(SANS_BOLD, 13)
    word = "BREACH"
    canvas.text((hub_x - canvas.textlength(word, font=hub_face) / 2, hub_y - 21),
                word, font=hub_face, fill=(255, 255, 255))
    small = load(SANS_BOLD, 11)
    word2 = "OSINT NETWORK"
    canvas.text((hub_x - canvas.textlength(word2, font=small) / 2, hub_y + 1),
                word2, font=small, fill=(255, 255, 255))


def story_card(canvas, x, y, w, h, section, headline, body):
    canvas.rounded_rectangle([x, y, x + w, y + h], radius=8,
                             outline=EDGE, width=1, fill=CARD)
    px, py = x + 16, y + 12
    canvas.text((px, py), section, font=load(SANS_BOLD, 13), fill=CRIMSON)
    py += 21
    head_face = load(SERIF_BOLD, 20)
    for line in fit_words(canvas, headline, head_face, w - 32):
        canvas.text((px, py), line, font=head_face, fill=BLACK)
        py += 25
    py += 3
    block_text(canvas, body, load(SANS_REG, 15), px, py, w - 32, 19,
               colour=(41, 39, 35), max_lines=5)


def build():
    sheet = Image.new("RGB", (PAGE_W, PAGE_H), CREAM)
    d = ImageDraw.Draw(sheet)

    # ---- masthead ----
    mast_face = load(SERIF_BOLD, 64)
    name = "THE WORLD"
    d.text(((PAGE_W - d.textlength(name, font=mast_face)) / 2, 12),
           name, font=mast_face, fill=BLACK)
    date_face = load(SANS_BOLD, 21)
    dateline = "WEDNESDAY  -  25 NOVEMBER 2026"
    d.text(((PAGE_W - d.textlength(dateline, font=date_face)) / 2, 90),
           dateline, font=date_face, fill=CRIMSON)
    d.line([(MARGIN, 124), (RIGHT, 124)], fill=BLACK, width=3)
    d.line([(MARGIN, 129), (RIGHT, 129)], fill=BLACK, width=1)

    # ---- lead story ----
    y = 144
    d.text((MARGIN, y), "TOP STORY  •  CYBERSECURITY",
           font=load(SANS_BOLD, 16), fill=CRIMSON)
    y += 26
    head_face = shrink_line(d, "CIA & ODNI BREACHED", SERIF_BOLD, 60,
                            RIGHT - MARGIN)
    d.text((MARGIN, y), "CIA & ODNI BREACHED", font=head_face, fill=BLACK)
    y += 72
    deck = ("Hackers hit the unclassified OSINT network — "
            "no classified data affected.")
    deck_face = shrink_line(d, deck, SERIF_ITAL, 21, RIGHT - MARGIN)
    d.text((MARGIN, y), deck, font=deck_face, fill=GREY)
    y += 34

    body_face = load(SANS_REG, 15)
    text_w = 592
    y = block_text(d, "Hackers broke into the unclassified network the CIA and "
                   "the Office of the Director of National Intelligence use to "
                   "analyse open-source intelligence — public material, social "
                   "media, satellite images and commercial data.",
                   body_face, MARGIN, y, text_w, 19)
    y += 7
    y = block_text(d, "No classified data was affected and no critical "
                   "capabilities were disrupted, the ODNI said. The CIA "
                   "declined to comment; the National Geospatial-Intelligence "
                   "Agency was also reported hit.",
                   body_face, MARGIN, y, text_w, 19)
    y += 7
    y = block_text(d, "Early signs point to China, two sources told CNN, though "
                   "it is unclear whether Beijing was involved. The suspected "
                   "tool is ARTEX, an AI hacking tool built by a Chinese engineer.",
                   body_face, MARGIN, y, text_w, 19)

    draw_diagram(d, 650, 274, RIGHT, 448)
    caption = "THE NETWORK THAT WAS HIT"
    cap_face = load(SANS_BOLD, 11)
    d.text((650 + (RIGHT - 650 - d.textlength(caption, font=cap_face)) / 2,
            452), caption, font=cap_face, fill=GREY)

    # ---- divider + supporting grid ----
    d.line([(MARGIN, 476), (RIGHT, 476)], fill=BLACK, width=2)
    stories = [
        ("MIDDLE EAST", "HOUTHIS HIT RIYADH'S TALLEST TOWER",
         "A Houthi drone strike hit the 80-storey Public Investment Fund "
         "Tower in Riyadh — the second attack in under a week. At least 11 "
         "people were wounded: 2 Saudis, 2 Indians, 3 Nepalis and 4 Egyptians. "
         "The Saudi-led coalition vowed a “decisive” response."),
        ("MARKETS", "NVIDIA SLIDES 5.9% AS AI RALLY REVERSES",
         "A day after a historic +31.5% surge, Nvidia closed down 5.9% on "
         "Tuesday. The chip index fell 7.9% and the Nasdaq lost 1.48%. In "
         "Asia on Wednesday the Nikkei fell 2.8%, the KOSPI more than 5% "
         "and SoftBank about 15%."),
        ("EUROPE", "POLAND PUSHES FOR PERMANENT US TROOPS",
         "Warsaw renewed its push for a permanent US military presence after "
         "two Russian airspace incursions in four days — three Kh-101 missiles "
         "on 20 Nov and a drone near Dorohusk on 23–24 Nov. NATO has approved "
         "AWACS deployments to Poland."),
        ("TECH & LAW", "HUAWEI GUILTY ON 10 OF 12 COUNTS",
         "A New York federal jury found Huawei guilty of 10 of 12 charges — "
         "trade-secret theft, bank fraud and conspiracy to defraud the US "
         "government — after a three-month trial. Huawei rejected the verdict."),
    ]
    cell_w = (RIGHT - MARGIN - 16) // 2
    cell_h = 188
    for idx, (section, headline, body) in enumerate(stories):
        cx = MARGIN + (idx % 2) * (cell_w + 16)
        cy = 490 + (idx // 2) * (cell_h + 12)
        story_card(d, cx, cy, cell_w, cell_h, section, headline, body)

    # ---- dark ticker ----
    d.rectangle([0, 888, PAGE_W, 998], fill=NAVY)
    d.text((MARGIN, 898), "ALSO TODAY", font=load(SANS_BOLD, 14), fill=GOLD)
    ticker_items = [
        "Amazon buys Decart tech in a reported $7.5bn deal",
        "OpenAI: GPT-6 designs new proteins",
        "Shein fined $100m in FTC settlement",
        "Colombia frees all hostages in Cartagena supermarket siege",
        "Shanghai party chief Chen Jining under investigation",
        "USTR prepares tariff probe of 16 trading partners",
    ]
    block_text(d, "   •   ".join(ticker_items), load(SANS_REG, 15),
               MARGIN, 922, RIGHT - MARGIN, 20, colour=(235, 235, 235))

    # ---- footer ----
    foot_face = load(SANS_REG, 11)
    foot = ("Sources: Reuters, CNN, AP, NYT, Nextgov  •  "
            "Events first reported on 25 November 2026")
    d.text(((PAGE_W - d.textlength(foot, font=foot_face)) / 2, 1004),
           foot, font=foot_face, fill=GREY)

    sheet.save(TARGET, "PNG", optimize=True)
    print("wrote", TARGET, sheet.size, os.path.getsize(TARGET), "bytes")


if __name__ == "__main__":
    build()
