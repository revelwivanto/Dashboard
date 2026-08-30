from components.styling import NAVY, ORANGE, CARD, BORDER, TEXT_MUTED


def _flow(steps: list[str], accent_last: bool = False) -> str:
    nodes = []
    for i, s in enumerate(steps):
        is_last = accent_last and i == len(steps) - 1
        bg = f"{ORANGE}1a" if is_last else CARD
        border = ORANGE if is_last else BORDER
        color = ORANGE if is_last else NAVY
        nodes.append(f'<div class="flow-node" style="background:{bg};border-color:{border};color:{color};">{s}</div>')
        if i < len(steps) - 1:
            nodes.append(f'<div class="flow-arrow">&#8594;</div>')
    return f"""
    <div class="flow-row">{''.join(nodes)}</div>
    <style>
      .flow-row {{ display:flex; align-items:center; flex-wrap:wrap; gap:2px; font-family:'Inter','Segoe UI',sans-serif; }}
      .flow-node {{ border:1.5px solid {BORDER}; border-radius:10px; padding:11px 15px; font-size:0.92rem;
                    font-weight:600; text-align:center; box-shadow:none; }}
      .flow-arrow {{ color:{TEXT_MUTED}; font-size:1.1rem; padding:0 6px; }}
    </style>
    """


def provenance_chain_html(chain: dict) -> str:
    steps = [
        f"Answer<br><span style='font-weight:400;font-size:0.82rem'>{chain['answer']}</span>",
        f"Citation<br><span style='font-weight:400;font-size:0.82rem'>{chain['citation']}</span>",
        f"Parent<br><span style='font-weight:400;font-size:0.82rem'>{chain['parent']}</span>",
        f"Document<br><span style='font-weight:400;font-size:0.82rem'>{chain['document']}</span>",
        f"{chain['page']}",
        f"Bounding box<br><span style='font-weight:400;font-size:0.82rem'>{chain['bbox']}</span>",
    ]
    return _flow(steps)


def tax_normalization_flow_html(observed_label: str, ppn_label: str, comparable_label: str) -> str:
    return _flow([
        f"Marketplace observed price<br><span style='font-weight:400;font-size:0.82rem'>{observed_label}</span>",
        f"Tax normalization<br><span style='font-weight:400;font-size:0.82rem'>{ppn_label}</span>",
        f"Comparable benchmark price<br><span style='font-weight:400;font-size:0.82rem'>{comparable_label}</span>",
    ])


def conditional_requirements_flow_html(steps: list[dict]) -> str:
    """The cr1..cr4 conditional-requirement chain on the Governance page.

    Each step is {code, label, value, sub}. Values are computed live from the
    target_uc* columns already carried in procurement_history.csv — this is a
    four-gate view of the same request, not four unrelated statistics.
    """
    nodes = []
    for s in steps:
        nodes.append(
            f"<span style='font-size:0.76rem;letter-spacing:0.08em;color:{ORANGE};"
            f"text-transform:uppercase;'>{s['code']}</span><br>"
            f"<span style='font-weight:400;font-size:0.85rem;'>{s['label']}</span><br>"
            f"<span style='font-size:1.45rem;font-weight:800;color:{NAVY};'>{s['value']}</span><br>"
            f"<span style='font-weight:400;font-size:0.75rem;color:{TEXT_MUTED};'>{s['sub']}</span>"
        )
    return _flow(nodes)


def business_story_cards_html(cards: list[dict]) -> str:
    """Business Story as three illustrated cards instead of plain text boxes."""
    blocks = []
    for c in cards:
        blocks.append(f"""
        <div class="story-card">
          <div class="story-icon" style="background:{c['color']}18;color:{c['color']};">{c['icon']}</div>
          <div class="story-title" style="color:{c['color']};">{c['title']}</div>
          <div class="story-steps">{''.join(
              f'<span class="story-step">{s}</span>'
              + (f'<span class="story-sep" style="color:{c["color"]};">&#8594;</span>' if i < len(c['steps']) - 1 else '')
              for i, s in enumerate(c['steps']))}</div>
        </div>""")
    return f"""
    <div class="story-row">{''.join(blocks)}</div>
    <style>
      .story-row {{ display:flex; gap:14px; flex-wrap:wrap; font-family:'Inter','Segoe UI',sans-serif; }}
      .story-card {{ flex:1 1 240px; background:{CARD}; border:1px solid {BORDER}; border-radius:14px;
                     padding:18px 20px; box-shadow:none; }}
      .story-icon {{ width:44px; height:44px; border-radius:12px; display:flex; align-items:center;
                     justify-content:center; font-size:1.7rem; margin-bottom:10px; }}
      .story-title {{ font-weight:800; font-size:1.08rem; margin-bottom:8px; }}
      .story-steps {{ display:flex; flex-wrap:wrap; align-items:center; gap:4px; }}
      .story-step {{ background:#F2F5F9; border:1px solid {BORDER}; border-radius:8px;
                     padding:5px 10px; font-size:0.85rem; color:{NAVY}; font-weight:600; }}
      .story-sep {{ font-size:0.85rem; font-weight:700; }}
    </style>
    """
