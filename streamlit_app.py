import json
import os
from datetime import datetime

import requests
import streamlit as st

# ==========================================================
# CONFIGURAÇÃO DO SUPABASE (preencher ou usar secrets)
# ==========================================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ==========================================================
# CSS CUSTOMIZADO - TEMA ESCURO GENSHIN
# ==========================================================
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
    }

    .account-card {
        background: rgba(30, 41, 59, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }

    .account-card:hover {
        border-color: #7C3AED;
        box-shadow: 0 10px 25px -5px rgba(124, 58, 237, 0.3);
        transform: translateY(-2px);
    }

    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .price-tag {
        font-size: 24px;
        font-weight: 800;
        color: #10B981;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
    }

    .resource-pill {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: center;
        font-size: 13px;
    }

    .resource-pill .value {
        font-size: 18px;
        font-weight: 700;
        color: #F8FAFC;
    }

    .resource-pill .label {
        font-size: 11px;
        color: #94A3B8;
        text-transform: uppercase;
    }

    .char-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid;
        border-radius: 8px;
        padding: 6px 10px;
        margin: 3px;
        font-size: 13px;
        font-weight: 600;
    }

    .section-title {
        font-size: 14px;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 16px 0 8px 0;
        border-bottom: 1px solid #334155;
        padding-bottom: 4px;
    }

    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid rgba(51, 65, 85, 0.3);
        font-size: 14px;
    }

    .detail-row .label { color: #94A3B8; }
    .detail-row .value { color: #F8FAFC; font-weight: 600; }

    .progress-bar {
        height: 6px;
        background: #1E293B;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 4px;
    }

    .progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;
    }

    .tag-pill {
        display: inline-block;
        background: #7C3AED;
        color: white;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }

    .header-glow {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(180deg, rgba(124,58,237,0.15) 0%, transparent 100%);
        border-radius: 0 0 24px 24px;
        margin-bottom: 30px;
    }

    .timestamp {
        text-align: center;
        color: #64748B;
        font-size: 12px;
        margin-top: 40px;
        padding: 20px;
    }

    /* Cores de elemento */
    .el-pyro { border-color: #DC2626; color: #FCA5A5; }
    .el-hydro { border-color: #0284C7; color: #7DD3FC; }
    .el-electro { border-color: #7C3AED; color: #C4B5FD; }
    .el-cryo { border-color: #38BDF8; color: #BAE6FD; }
    .el-geo { border-color: #D97706; color: #FCD34D; }
    .el-anemo { border-color: #0D9488; color: #5EEAD4; }
    .el-dendro { border-color: #16A34A; color: #86EFAC; }

    /* Status colors */
    .st-disponivel { background: #059669; color: white; }
    .st-reservada { background: #F59E0B; color: #111827; }
    .st-vendida { background: #6B7280; color: white; }
    .st-pausada { background: #7C3AED; color: white; }
    .st-farmando { background: #0891B2; color: white; }
    .st-revisar { background: #DC2626; color: white; }
</style>
"""

# ==========================================================
# ELEMENTOS / UTILS
# ==========================================================
ELEMENT_ICONS = {
    "Pyro": "🔥", "Hydro": "💧", "Electro": "⚡", "Cryo": "❄️",
    "Geo": "🟡", "Anemo": "🌪️", "Dendro": "🌿"
}

ELEMENT_CLASSES = {
    "Pyro": "el-pyro", "Hydro": "el-hydro", "Electro": "el-electro",
    "Cryo": "el-cryo", "Geo": "el-geo", "Anemo": "el-anemo", "Dendro": "el-dendro"
}

STATUS_CLASSES = {
    "Disponível": "st-disponivel", "Reservada": "st-reservada", "Vendida": "st-vendida",
    "Pausada": "st-pausada", "Farmando": "st-farmando", "Revisar": "st-revisar"
}

MAP_AREAS = [
    ("mondstadt", "Mondstadt"), ("dragonspine", "Espinha do Dragão"),
    ("liyue", "Liyue"), ("chasm_surface", "Despenhadeiro - Sup."),
    ("chasm_underground", "Despenhadeiro - Sub."), ("chenyu_vale", "Vale Chenyu"),
    ("inazuma", "Inazuma"), ("enkanomiya", "Enkanomiya"),
    ("sumeru_rainforest", "Sumeru - Floresta"), ("sumeru_desert", "Sumeru - Deserto"),
    ("hadramaveth", "Hadramaveth"), ("girdle_of_the_sands", "Cinturão das Areias"),
    ("fontaine", "Fontaine"), ("sea_of_bygone_eras", "Mar das Eras Passadas"),
    ("natlan", "Natlan"), ("sacred_mountain", "Montanha Sagrada"),
    ("ancient_temple", "Templo Antigo"),
]

# ==========================================================
# FUNÇÕES DE API
# ==========================================================
@st.cache_data(ttl=30)
def fetch_accounts():
    """Busca contas visíveis do Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        url = f"{SUPABASE_URL}/rest/v1/public_accounts?is_visible=eq.true&order=updated_at.desc"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception:
        return []


def parse_json_field(data, field):
    """Parseia campo JSON do Supabase."""
    try:
        val = data.get(field)
        if isinstance(val, str):
            return json.loads(val)
        return val or []
    except Exception:
        return []


def parse_json_dict(data, field):
    """Parseia campo JSON dict do Supabase."""
    try:
        val = data.get(field)
        if isinstance(val, str):
            return json.loads(val)
        return val or {}
    except Exception:
        return {}


# ==========================================================
# COMPONENTES DE UI
# ==========================================================
def render_resource_pill(icon, label, value):
    return f"""
    <div class="resource-pill">
        <div class="value">{icon} {value}</div>
        <div class="label">{label}</div>
    </div>
    """


def render_character_chip(char):
    name = char.get("character_name", "?")
    element = char.get("element", "")
    constellation = char.get("constellation", "C0")
    el_icon = ELEMENT_ICONS.get(element, "✦")
    el_class = ELEMENT_CLASSES.get(element, "")
    return f"""
    <span class="char-chip {el_class}">
        {el_icon} {name} <strong>{constellation}</strong>
    </span>
    """


def render_account_card(account):
    """Renderiza um card completo de conta."""
    name = account.get("name", "Conta sem nome")
    uid = account.get("uid", "-")
    server = account.get("server", "-")
    status = account.get("status", "-")
    ar = account.get("ar", 0)
    wl = account.get("world_level", 0)
    price = account.get("price", "-")
    tags = account.get("tags", "")

    primogems = account.get("primogems", 0)
    intertwined = account.get("intertwined_wishes", 0)
    acquaint = account.get("acquaint_wishes", 0)
    starglitter = account.get("starglitter", 0)
    stardust = account.get("stardust", 0)
    resin = account.get("fragile_resin", 0)

    characters = parse_json_field(account, "characters_json")
    weapons = parse_json_field(account, "weapons_json")
    map_progress = parse_json_dict(account, "map_progress_json")

    abyss_floor = account.get("abyss_floor", "-")
    birthday = "Sim" if account.get("birthday_set") else "Não"
    abyss = "Sim" if account.get("abyss_unlocked") else "Não"
    extra = account.get("extra_info", "")

    status_class = STATUS_CLASSES.get(status, "")
    status_badge = f'<span class="status-badge {status_class}">{status}</span>'

    # Personagens chips
    chars_html = " ".join([render_character_chip(c) for c in characters[:8]])
    if len(characters) > 8:
        chars_html += f'<span style="color:#64748B;font-size:12px;margin-left:6px;">+{len(characters)-8} mais</span>'

    # Tags
    tags_html = ""
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        tags_html = " ".join([f'<span class="tag-pill">{t}</span>' for t in tag_list])

    # Recursos grid
    resources_html = f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:12px 0;">
        {render_resource_pill("💎", "Primogems", f"{primogems:,}")}
        {render_resource_pill("🌠", "Limitados", intertwined)}
        {render_resource_pill("⭐", "Padrão", acquaint)}
        {render_resource_pill("✨", "Starglitter", starglitter)}
        {render_resource_pill("🌙", "Stardust", stardust)}
        {render_resource_pill("⚡", "Resina", resin)}
    </div>
    """

    # Progresso de mapa
    map_html = ""
    for key, label in MAP_AREAS:
        val = map_progress.get(key, 0)
        if val > 0:
            color = "#7C3AED" if val >= 80 else "#0DCAF0" if val >= 50 else "#94A3B8"
            map_html += f"""
            <div style="margin:4px 0;">
                <div style="display:flex;justify-content:space-between;font-size:12px;">
                    <span style="color:#CBD5E1;">{label}</span>
                    <span style="color:{color};font-weight:700;">{val}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{val}%;background:{color};"></div>
                </div>
            </div>
            """

    # Armas (detalhe)
    weapons_html = ""
    if weapons:
        for w in weapons[:6]:
            wname = w.get("weapon_name", "?")
            wchar = w.get("character_name", "-")
            wref = w.get("refinement", "R1")
            weapons_html += f'<div class="detail-row"><span class="label">⚔️ {wname}</span><span class="value">{wchar} • {wref}</span></div>'
        if len(weapons) > 6:
            weapons_html += f'<div style="color:#64748B;font-size:12px;text-align:center;padding:4px;">+{len(weapons)-6} armas</div>'

    # Card principal
    card_html = f"""
    <div class="account-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
            <div>
                <h3 style="margin:0;color:#F8FAFC;font-size:20px;">{name}</h3>
                <div style="color:#94A3B8;font-size:13px;margin-top:4px;">
                    UID: {uid} • {server} • AR {ar} • WL {wl}
                </div>
            </div>
            <div style="text-align:right;">
                {status_badge}
                <div class="price-tag" style="margin-top:8px;">{price}</div>
            </div>
        </div>

        {tags_html}

        <div class="section-title">Recursos</div>
        {resources_html}

        <div class="section-title">Personagens ({len(characters)})</div>
        <div style="margin:8px 0;">{chars_html}</div>

        <details style="margin-top:16px;">
            <summary style="color:#7C3AED;font-weight:700;cursor:pointer;font-size:14px;">
                🔍 Ver detalhes completos
            </summary>
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid #334155;">

                <div class="section-title">Progresso</div>
                <div class="detail-row"><span class="label">Aniversário definido</span><span class="value">{birthday}</span></div>
                <div class="detail-row"><span class="label">Abismo liberado</span><span class="value">{abyss}</span></div>
                <div class="detail-row"><span class="label">Andar máximo</span><span class="value">{abyss_floor}</span></div>

                <div class="section-title">Exploração</div>
                {map_html if map_html else '<div style="color:#64748B;font-size:13px;">Sem dados de exploração</div>'}

                <div class="section-title">Armas ({len(weapons)})</div>
                {weapons_html if weapons_html else '<div style="color:#64748B;font-size:13px;">Sem armas cadastradas</div>'}

                {f'<div class="section-title">Observações</div><div style="background:#0B1220;padding:12px;border-radius:8px;color:#CBD5E1;font-size:13px;white-space:pre-wrap;">{extra}</div>' if extra else ''}

                <div style="margin-top:12px;text-align:center;">
                    <span style="color:#64748B;font-size:12px;">Atualizado em: {account.get("updated_at", "-")[:16]}</span>
                </div>
            </div>
        </details>
    </div>
    """
    return card_html


# ==========================================================
# APP PRINCIPAL
# ==========================================================
def main():
    st.set_page_config(
        page_title="Genshin Impact - Contas à Venda",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="header-glow">
        <h1 style="margin:0;color:#F8FAFC;font-size:42px;font-weight:800;">
            ⚔️ Genshin Impact
        </h1>
        <p style="margin:8px 0 0 0;color:#94A3B8;font-size:18px;">
            Contas disponíveis para venda • Atualizado em tempo real
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar - Filtros
    with st.sidebar:
        st.markdown("<h2 style='color:#F8FAFC;'>🔍 Filtros</h2>", unsafe_allow_html=True)

        search = st.text_input("Buscar por nome, UID ou personagem", "")

        status_filter = st.multiselect(
            "Status",
            ["Disponível", "Reservada", "Vendida", "Pausada", "Farmando", "Revisar"],
            default=["Disponível"]
        )

        server_filter = st.multiselect(
            "Servidor",
            ["America", "Europe", "Asia", "TW/HK/MO", "Outro"],
            default=[]
        )

        min_ar, max_ar = st.slider("Adventure Rank (AR)", 1, 60, (1, 60))

        price_sort = st.selectbox(
            "Ordenar por",
            ["Mais recente", "Menor preço", "Maior AR", "Mais personagens"]
        )

        st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)

        if st.button("🔄 Atualizar agora", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("""
        <div style="margin-top:30px;padding:16px;background:#1E293B;border-radius:12px;border:1px solid #334155;">
            <h4 style="color:#F8FAFC;margin:0 0 8px 0;">📞 Contato</h4>
            <p style="color:#94A3B8;font-size:13px;margin:0;">
                Interessado em alguma conta?<br>
                Entre em contato pelo Discord/WhatsApp.<br><br>
                <strong style="color:#7C3AED;">As contas são verificadas e entregues com segurança.</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Buscar dados
    accounts = fetch_accounts()

    if not accounts:
        st.warning("⚠️ Nenhuma conta disponível no momento. Volte em breve!")
        if not SUPABASE_URL:
            st.error("🔧 Configuração incompleta: SUPABASE_URL não definido.")
        st.markdown("""
        <div class="timestamp">
            Vitrine v2.0 • Genshin Account Manager Pro
        </div>
        """, unsafe_allow_html=True)
        return

    # Filtros
    filtered = []
    for acc in accounts:
        # Status
        if status_filter and acc.get("status") not in status_filter:
            continue
        # Servidor
        if server_filter and acc.get("server") not in server_filter:
            continue
        # AR
        ar = acc.get("ar", 0)
        if ar < min_ar or ar > max_ar:
            continue
        # Busca textual
        if search:
            search_lower = search.lower()
            blob = f"{acc.get('name','')} {acc.get('uid','')} {acc.get('tags','')}"
            chars = parse_json_field(acc, "characters_json")
            for c in chars:
                blob += f" {c.get('character_name','')}"
            if search_lower not in blob.lower():
                continue
        filtered.append(acc)

    # Ordenação
    if price_sort == "Menor preço":
        # Tenta extrair número do preço
        def extract_price(a):
            p = str(a.get("price", "0"))
            nums = "".join([c for c in p if c.isdigit() or c == "."])
            try:
                return float(nums) if nums else 999999
            except:
                return 999999
        filtered.sort(key=extract_price)
    elif price_sort == "Maior AR":
        filtered.sort(key=lambda x: x.get("ar", 0), reverse=True)
    elif price_sort == "Mais personagens":
        def count_chars(a):
            return len(parse_json_field(a, "characters_json"))
        filtered.sort(key=count_chars, reverse=True)
    # else: mais recente (já vem ordenado do Supabase)

    # Stats
    total = len(filtered)
    total_5star = sum(len(parse_json_field(a, "characters_json")) for a in filtered)

    col1, col2, col3 = st.columns(3)
    col1.metric("Contas disponíveis", total)
    col2.metric("Total de personagens 5★", total_5star)
    col3.metric("Servidores", len(set(a.get("server") for a in filtered)))

    st.markdown("<hr style='border-color:#334155;margin:20px 0;'>", unsafe_allow_html=True)

    # Grid de cards
    if not filtered:
        st.info("Nenhuma conta encontrada com os filtros selecionados.")
    else:
        cols = st.columns(2)
        for idx, account in enumerate(filtered):
            with cols[idx % 2]:
                import streamlit.components.v1 as components
                    components.html(render_account_card(account), height=600, scrolling=True)

    # Footer
    st.markdown(f"""
    <div class="timestamp">
        Vitrine v2.0 • Genshin Account Manager Pro • Última atualização: {datetime.now().strftime('%H:%M:%S')}<br>
        <span style="font-size:11px;">As informações são atualizadas automaticamente pelo vendedor.</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
