import json
import os
import base64
from datetime import datetime

import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================================
# CONFIGURAÇÃO DO SUPABASE
# ==========================================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ==========================================================
# CSS GLOBAL - Flip Card e Tema
# ==========================================================
FLIP_CARD_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body {
        font-family: 'Inter', sans-serif;
        background: #0a0a1a !important;
    }

    .main, .stApp {
        background: #0a0a1a !important;
    }

    /* Flip Card Container */
    .flip-card {
        background-color: transparent;
        width: 100%;
        height: 420px;
        perspective: 1000px;
        margin-bottom: 20px;
    }

    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        transform-style: preserve-3d;
    }

    .flip-card.flipped .flip-card-inner {
        transform: rotateY(180deg);
    }

    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }

    /* Frente do Card */
    .flip-card-front {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(124, 58, 237, 0.3);
        display: flex;
        flex-direction: column;
    }

    .flip-card-front:hover {
        border-color: rgba(124, 58, 237, 0.6);
        box-shadow: 0 8px 32px rgba(124, 58, 237, 0.2);
    }

    /* Verso do Card */
    .flip-card-back {
        background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
        border: 1px solid rgba(124, 58, 237, 0.5);
        transform: rotateY(180deg);
        overflow-y: auto;
        padding: 20px;
    }

    /* Imagem de capa */
    .card-image {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-bottom: 2px solid rgba(124, 58, 237, 0.3);
    }

    .card-image-placeholder {
        width: 100%;
        height: 180px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        border-bottom: 2px solid rgba(124, 58, 237, 0.3);
    }

    /* Conteúdo da frente */
    .card-front-content {
        padding: 16px;
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .card-title {
        font-size: 22px;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0 0 8px 0;
        text-align: left;
    }

    .card-meta {
        font-size: 13px;
        color: #94A3B8;
        text-align: left;
        margin-bottom: 12px;
    }

    .card-price {
        font-size: 28px;
        font-weight: 800;
        color: #10B981;
        text-align: left;
        margin: 8px 0;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
    }

    .card-status {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }

    .card-status.disponivel { background: #059669; color: white; }
    .card-status.reservada { background: #F59E0B; color: #111827; }
    .card-status.vendida { background: #6B7280; color: white; }
    .card-status.pausada { background: #7C3AED; color: white; }
    .card-status.farmando { background: #0891B2; color: white; }
    .card-status.revisar { background: #EF4444; color: white; }

    .card-chars {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }

    .char-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid;
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 12px;
        font-weight: 600;
        color: #F8FAFC;
    }

    .char-chip .const {
        font-size: 10px;
        opacity: 0.8;
    }

    .card-btn {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        cursor: pointer;
        width: 100%;
        margin-top: 12px;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
    }

    .card-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5);
    }

    /* Verso - Detalhes */
    .back-title {
        font-size: 20px;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 16px;
        text-align: center;
        border-bottom: 1px solid rgba(124, 58, 237, 0.3);
        padding-bottom: 12px;
    }

    .back-section {
        margin-bottom: 16px;
        text-align: left;
    }

    .back-section-title {
        font-size: 13px;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        padding-bottom: 4px;
    }

    .resource-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
    }

    .resource-item {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
    }

    .resource-item .value {
        font-size: 18px;
        font-weight: 700;
        color: #F8FAFC;
    }

    .resource-item .label {
        font-size: 10px;
        color: #94A3B8;
        text-transform: uppercase;
    }

    .progress-item {
        margin-bottom: 6px;
    }

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

    .back-btn {
        background: rgba(124, 58, 237, 0.2);
        color: #C4B5FD;
        border: 1px solid rgba(124, 58, 237, 0.5);
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        cursor: pointer;
        width: 100%;
        margin-top: 16px;
        transition: all 0.3s;
    }

    .back-btn:hover {
        background: rgba(124, 58, 237, 0.4);
        color: white;
    }

    /* Scrollbar do verso */
    .flip-card-back::-webkit-scrollbar {
        width: 6px;
    }
    .flip-card-back::-webkit-scrollbar-track {
        background: transparent;
    }
    .flip-card-back::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 3px;
    }

    /* Grid de cards */
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 20px;
        padding: 10px 0;
    }
</style>
"""

# ==========================================================
# CORES
# ==========================================================
ELEMENT_COLORS = {
    "Pyro": "#DC2626", "Hydro": "#0284C7", "Electro": "#7C3AED",
    "Cryo": "#38BDF8", "Geo": "#D97706", "Anemo": "#0D9488", "Dendro": "#16A34A"
}

STATUS_CLASSES = {
    "Disponível": "disponivel", "Reservada": "reservada", "Vendida": "vendida",
    "Pausada": "pausada", "Farmando": "farmando", "Revisar": "revisar"
}

ELEMENT_ICONS = {
    "Pyro": "🔥", "Hydro": "💧", "Electro": "⚡", "Cryo": "❄️",
    "Geo": "🟡", "Anemo": "🌪️", "Dendro": "🌿"
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
    try:
        val = data.get(field)
        if isinstance(val, str):
            return json.loads(val)
        return val or []
    except Exception:
        return []


def parse_json_dict(data, field):
    try:
        val = data.get(field)
        if isinstance(val, str):
            return json.loads(val)
        return val or {}
    except Exception:
        return {}


# ==========================================================
# GERAR HTML DO FLIP CARD
# ==========================================================
def generate_flip_card(account, idx):
    """Gera HTML/CSS/JS de um flip card completo."""
    name = account.get("name", "Conta sem nome")
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
    cover_b64 = account.get("cover_image_base64", "")

    status_class = STATUS_CLASSES.get(status, "disponivel")

    # Imagem
    if cover_b64:
        img_html = f'<img src="data:image/jpeg;base64,{cover_b64}" class="card-image" alt="Capa">'
    else:
        img_html = '<div class="card-image-placeholder">📷</div>'

    # Personagens chips (frente)
    chars_front = ""
    for char in characters[:6]:
        el = char.get("element", "")
        el_color = ELEMENT_COLORS.get(el, "#334155")
        el_icon = ELEMENT_ICONS.get(el, "✦")
        c_name = char.get("character_name", "?")
        c_const = char.get("constellation", "")
        chars_front += f'<span class="char-chip" style="border-color: {el_color};">{el_icon} {c_name} <span class="const">{c_const}</span></span>'
    if len(characters) > 6:
        chars_front += f'<span style="color:#64748B;font-size:11px;margin-left:4px;">+{len(characters)-6}</span>'

    # Tags
    tags_html = ""
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()][:3]
        tags_html = " ".join([f'<span style="background:rgba(124,58,237,0.3);color:#C4B5FD;padding:2px 8px;border-radius:4px;font-size:11px;margin-right:4px;border:1px solid rgba(124,58,237,0.5);">{t}</span>' for t in tag_list])

    # Recursos (verso)
    resources_html = f"""
    <div class="resource-grid">
        <div class="resource-item"><div class="value">💎 {primogems:,}</div><div class="label">Primogems</div></div>
        <div class="resource-item"><div class="value">🌠 {intertwined}</div><div class="label">Limitados</div></div>
        <div class="resource-item"><div class="value">⭐ {acquaint}</div><div class="label">Padrão</div></div>
        <div class="resource-item"><div class="value">✨ {starglitter}</div><div class="label">Starglitter</div></div>
        <div class="resource-item"><div class="value">🌙 {stardust}</div><div class="label">Stardust</div></div>
        <div class="resource-item"><div class="value">⚡ {resin}</div><div class="label">Resina</div></div>
    </div>
    """

    # Progresso (verso)
    progress_html = f"""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px;">
        <div class="resource-item"><div class="value">🎂</div><div class="label">{birthday}</div></div>
        <div class="resource-item"><div class="value">🏰</div><div class="label">{abyss}</div></div>
        <div class="resource-item"><div class="value">📈</div><div class="label">{abyss_floor}</div></div>
    </div>
    """

    # Exploração (verso)
    map_html = ""
    for key, label in MAP_AREAS:
        val = map_progress.get(key, 0)
        if val > 0:
            color = "#7C3AED" if val >= 80 else "#0DCAF0" if val >= 50 else "#64748B"
            map_html += f"""
            <div class="progress-item">
                <div style="display:flex;justify-content:space-between;font-size:12px;color:#CBD5E1;">
                    <span>{label}</span>
                    <span style="color:{color};font-weight:700;">{val}%</span>
                </div>
                <div class="progress-bar"><div class="progress-fill" style="width:{val}%;background:{color};"></div></div>
            </div>
            """

    # Armas (verso)
    weapons_html = ""
    if weapons:
        for w in weapons[:8]:
            wname = w.get("weapon_name", "?")
            wchar = w.get("character_name", "-")
            wref = w.get("refinement", "R1")
            weapons_html += f'<div style="font-size:13px;color:#CBD5E1;margin-bottom:4px;">⚔️ <strong>{wname}</strong> ({wchar}) {wref}</div>'
        if len(weapons) > 8:
            weapons_html += f'<div style="color:#64748B;font-size:11px;">+{len(weapons)-8} armas</div>'

    # Observações
    extra_html = ""
    if extra:
        extra_html = f'<div style="background:rgba(15,23,42,0.8);border:1px solid #334155;border-radius:8px;padding:10px;font-size:13px;color:#CBD5E1;margin-top:8px;white-space:pre-wrap;">{extra}</div>'

    card_id = f"card_{idx}"

    html = f"""
    <div class="flip-card" id="{card_id}">
        <div class="flip-card-inner">
            <!-- FRENTE -->
            <div class="flip-card-front">
                {img_html}
                <div class="card-front-content">
                    <div>
                        <div class="card-status {status_class}">{status}</div>
                        <h3 class="card-title">{name}</h3>
                        <div class="card-meta">🌐 {server} • ⭐ AR {ar} • WL {wl}</div>
                        {tags_html}
                        <div class="card-chars">{chars_front}</div>
                    </div>
                    <div>
                        <div class="card-price">💰 {price}</div>
                        <button class="card-btn" onclick="document.getElementById('{card_id}').classList.add('flipped')">
                            🔍 Ver detalhes
                        </button>
                    </div>
                </div>
            </div>

            <!-- VERSO -->
            <div class="flip-card-back">
                <h3 class="back-title">{name}</h3>

                <div class="back-section">
                    <div class="back-section-title">📦 Recursos</div>
                    {resources_html}
                </div>

                <div class="back-section">
                    <div class="back-section-title">📊 Progresso</div>
                    {progress_html}
                </div>

                <div class="back-section">
                    <div class="back-section-title">🗺️ Exploração</div>
                    {map_html}
                </div>

                <div class="back-section">
                    <div class="back-section-title">⚔️ Armas ({len(weapons)})</div>
                    {weapons_html}
                </div>

                {extra_html}

                <button class="back-btn" onclick="document.getElementById('{card_id}').classList.remove('flipped')">
                    ← Voltar
                </button>
            </div>
        </div>
    </div>
    """
    return html


# ==========================================================
# APP PRINCIPAL
# ==========================================================
def main():
    st.set_page_config(
        page_title="Genshin Impact - Catálogo de Contas",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(FLIP_CARD_CSS, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 30px 20px 20px;">
        <h1 style="margin:0; color:#F8FAFC; font-size: 36px; font-weight: 800;">⚔️ Catálogo de Contas</h1>
        <p style="margin:8px 0 0 0; color:#94A3B8; font-size: 16px;">Genshin Impact • Contas verificadas</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar - Filtros
    with st.sidebar:
        st.markdown("<h3 style='color:#F8FAFC;'>🔍 Filtros</h3>", unsafe_allow_html=True)

        search = st.text_input("Buscar", "", placeholder="Nome, personagem...")

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

        min_ar, max_ar = st.slider("AR", 1, 60, (1, 60))

        price_sort = st.selectbox(
            "Ordenar",
            ["Mais recente", "Menor preço", "Maior AR", "Mais personagens"]
        )

        st.divider()

        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("""
        <div style="margin-top:20px; padding:16px; background:#1E293B; border-radius:12px; border:1px solid #334155;">
            <h4 style="color:#F8FAFC; margin:0 0 8px 0;">📞 Contato</h4>
            <p style="color:#94A3B8; font-size:13px; margin:0;">
                Interessado? Entre em contato!<br><br>
                <strong style="color:#7C3AED;">Contas verificadas e entregues com segurança.</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Buscar dados
    accounts = fetch_accounts()

    if not accounts:
        st.warning("⚠️ Nenhuma conta disponível no momento.")
        if not SUPABASE_URL:
            st.error("🔧 SUPABASE_URL não definido.")
        return

    # Filtros
    filtered = []
    for acc in accounts:
        if status_filter and acc.get("status") not in status_filter:
            continue
        if server_filter and acc.get("server") not in server_filter:
            continue
        ar = acc.get("ar", 0)
        if ar < min_ar or ar > max_ar:
            continue
        if search:
            search_lower = search.lower()
            blob = f"{acc.get('name','')} {acc.get('tags','')}"
            chars = parse_json_field(acc, "characters_json")
            for c in chars:
                blob += f" {c.get('character_name','')}"
            if search_lower not in blob.lower():
                continue
        filtered.append(acc)

    # Ordenação
    if price_sort == "Menor preço":
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

    # Contador
    st.markdown(f"<p style='color:#94A3B8;margin-bottom:20px;'>📦 {len(filtered)} contas encontradas</p>", unsafe_allow_html=True)

    st.divider()

    # Grid de Flip Cards
    if not filtered:
        st.info("Nenhuma conta encontrada com os filtros.")
    else:
        # CSS Grid via HTML
        cards_html = '<div class="cards-grid">'
        for idx, account in enumerate(filtered):
            cards_html += generate_flip_card(account, idx)
        cards_html += '</div>'

        components.html(cards_html, height=480 * ((len(filtered) + 2) // 3), scrolling=True)

    # Footer
    st.markdown(f"""
    <div style="text-align:center; color:#64748B; font-size:12px; margin-top:40px; padding:20px; border-top:1px solid #1E293B;">
        Genshin Account Manager Pro • Última atualização: {datetime.now().strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
