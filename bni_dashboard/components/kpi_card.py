"""Executive KPI cards with a small count-up animation. Pure presentation —
all numbers are passed in already computed from the data layer, nothing
is invented here.

Layout note (per the DashboardRevisions markup): the short caption sits
ABOVE the number, and data-type badges are off by default. Pass an explicit
`data_type` only where a badge is genuinely wanted.
"""
import streamlit.components.v1 as components
from components.styling import NAVY, ORANGE, TEXT_MUTED, CARD, BORDER, DATA_TYPE_COLORS

_BADGE_LABELS = {
    "observed": "Observed / Real", "synthetic": "Synthetic", "illustrative": "Illustrative",
    "assumption": "Assumption", "assumption-based": "Assumption-based",
    "calculated": "Calculated", "regulatory_fact": "Regulatory Fact",
}


def kpi_row(cards: list[dict], height: int | None = None):
    """cards: [{label, value, prefix, suffix, decimals, data_type, note}]

    `value=None` renders a static placeholder (default "—") instead of an
    animated number — used for a KPI whose formula is still pending.

    The row lives in a fixed-height iframe with scrolling off, so anything
    taller than `height` is silently cut — a card whose note wraps loses its
    footer, and a card pushed onto a second flex line disappears entirely.
    When no height is given, size it from the longest note instead of a
    constant so a card can never be clipped out of existence.
    """
    if height is None:
        longest_note = max((len(c.get("note", "")) for c in cards), default=0)
        longest_label = max((len(c.get("label", "")) for c in cards), default=0)
        # Type is a step larger than it was, so the per-line allowances grew
        # with it: ~26 chars per label line at 0.92rem, ~30 per note line at
        # 0.8rem. Undersizing here silently clips a card's footer.
        label_lines = max(1, (longest_label + 25) // 26)
        note_lines = ((longest_note + 29) // 30) if longest_note else 0
        height = 104 + 20 * label_lines + (28 + 15 * note_lines if note_lines else 0)

    card_html = []
    for i, c in enumerate(cards):
        data_type = c.get("data_type")
        note = c.get("note", "")
        badge = ""
        if data_type:
            color = DATA_TYPE_COLORS.get(data_type, TEXT_MUTED)
            badge = (f'<div class="kpi-badge" style="background:{color}1a;color:{color};'
                     f'border:1px solid {color}55;">{_BADGE_LABELS.get(data_type, data_type)}</div>')

        if c.get("value") is None:
            value_html = f'<div class="kpi-value kpi-pending">{c.get("placeholder", "—")}</div>'
        else:
            value_html = (f'<div class="kpi-value" data-target="{c["value"]}" '
                          f'data-decimals="{c.get("decimals", 0)}" '
                          f'data-prefix="{c.get("prefix", "")}" data-suffix="{c.get("suffix", "")}" '
                          f'id="kpi-{i}">0</div>')

        card_html.append(f"""
        <div class="kpi-card">
          {badge}
          <div class="kpi-label">{c['label']}</div>
          {value_html}
          {f'<div class="kpi-note">{note}</div>' if note else ''}
        </div>""")

    html = f"""
    <div class="kpi-row">{''.join(card_html)}</div>
    <style>
      .kpi-row {{ display:flex; gap:14px; flex-wrap:wrap; font-family:'Inter','Segoe UI',sans-serif; }}
      .kpi-card {{ flex:1 1 0; min-width:158px; background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
                   padding:16px 18px; box-shadow:none; position:relative; }}
      .kpi-badge {{ display:inline-block; padding:2px 9px; border-radius:999px; font-size:0.7rem;
                    font-weight:700; letter-spacing:0.03em; text-transform:uppercase; margin-bottom:10px; }}
      .kpi-label {{ color:{NAVY}; font-size:1.02rem; font-weight:700; line-height:1.35; margin-bottom:6px; }}
      .kpi-value {{ font-size:2.35rem; font-weight:800; color:{NAVY}; line-height:1.1; }}
      .kpi-pending {{ color:{TEXT_MUTED}; }}
      .kpi-note {{ color:{TEXT_MUTED}; font-size:0.88rem; margin-top:7px; border-top:1px dashed {BORDER}; padding-top:7px; }}
    </style>
    <script>
      const els = document.querySelectorAll('.kpi-value[data-target]');
      els.forEach(el => {{
        const target = parseFloat(el.getAttribute('data-target'));
        const decimals = parseInt(el.getAttribute('data-decimals'));
        const prefix = el.getAttribute('data-prefix');
        const suffix = el.getAttribute('data-suffix');
        let cur = 0;
        const steps = 40;
        const inc = target / steps;
        let n = 0;
        const timer = setInterval(() => {{
          n += 1; cur += inc;
          if (n >= steps) {{ cur = target; clearInterval(timer); }}
          el.textContent = prefix + cur.toLocaleString('id-ID', {{minimumFractionDigits: decimals, maximumFractionDigits: decimals}}) + suffix;
        }}, 16);
      }});
    </script>
    """
    components.html(html, height=height, scrolling=False)
