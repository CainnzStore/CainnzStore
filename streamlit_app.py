import json
import os
from datetime import datetime

import requests
import streamlit as st

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
# CSS CUSTOMIZADO MINIMAL
# ==========================================================
CUSTOM_CSS = """
<style>
    .main {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #F8FAFC !important;
    }
    .stMarkdown {
        color: #F8FAFC;
    }
    .st-emotion-cache-1y4p8pa {
        max-width: 1200px;
    }
</style>
"""

# ==========================================================
# ELEMENTOS / CORES
# ==========================================================
ELEMENT_COLORS = {
    "Pyro": "#DC2626", "Hydro": "#0284C7", "Electro": "#7C3AED",
    "Cryo": "#38BDF8", "Geo": "#D97706", "Anemo": "#0D9488", "Dendro": "#16A34A"
}

STATUS_COLORS = {
    "Disponível": "#059669", "Reservada": "#F59E0B", "Vendida": "#6B7280",
    "Pausada": "#7C3AED", "Farmando": "#0891B2", "Revisar": "#DC2626"
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
# COMPONENTES DE UI
# ==========================================================
def render_account_card(account):
    """Renderiza um card de conta usando componentes nativos do Streamlit."""
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
    has_cover = account.get("has_cover", False)

    status_color = STATUS_COLORS.get(status, "#334155")

    # CARD PRINCIPAL
    with st.container():
        # Container com borda customizada
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.9); border: 1px solid #334155; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        </div>
        """, unsafe_allow_html=True)

        # Header: Nome + Status + Preço
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.markdown(f"### {name}")
            st.markdown(f"**UID:** {uid} • **Servidor:** {server} • **AR** {ar} • **WL** {wl}")
        with col_header2:
            # Status badge
            st.markdown(f"""
            <div style="background: {status_color}; color: white; padding: 6px 14px; border-radius: 20px; text-align: center; font-weight: bold; font-size: 13px; margin-bottom: 8px;">
                {status.upper()}
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #10B981; text-align: center; margin: 0;'>💰 {price}</h2>", unsafe_allow_html=True)

        # Tags
        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            tags_html = " ".join([f'<span style="background: #7C3AED; color: white; padding: 3px 10px; border-radius: 6px; font-size: 12px; margin-right: 5px;">{t}</span>' for t in tag_list])
            st.markdown(tags_html, unsafe_allow_html=True)

        st.divider()

        # RECURSOS
        st.markdown("**📦 Recursos**")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("💎 Primogems", f"{primogems:,}")
        with r2:
            st.metric("🌠 Limitados", intertwined)
        with r3:
            st.metric("⭐ Padrão", acquaint)

        r4, r5, r6 = st.columns(3)
        with r4:
            st.metric("✨ Starglitter", starglitter)
        with r5:
            st.metric("🌙 Stardust", stardust)
        with r6:
            st.metric("⚡ Resina", resin)

        st.divider()

        # PERSONAGENS
        st.markdown(f"**🎭 Personagens ({len(characters)})**")
        if characters:
            char_cols = st.columns(min(len(characters), 6))
            for idx, char in enumerate(characters[:6]):
                with char_cols[idx % 6]:
                    el = char.get("element", "")
                    el_color = ELEMENT_COLORS.get(el, "#334155")
                    el_icon = ELEMENT_ICONS.get(el, "✦")
                    c_name = char.get("character_name", "?")
                    c_const = char.get("constellation", "C0")
                    st.markdown(f"""
                    <div style="border: 2px solid {el_color}; border-radius: 10px; padding: 8px; text-align: center; background: rgba(15,23,42,0.6);">
                        <div style="font-size: 20px;">{el_icon}</div>
                        <div style="font-weight: bold; font-size: 13px; color: #F8FAFC;">{c_name}</div>
                        <div style="color: {el_color}; font-size: 12px; font-weight: bold;">{c_const}</div>
                    </div>
                    """, unsafe_allow_html=True)
            if len(characters) > 6:
                st.caption(f"+{len(characters)-6} personagens")

        # DETALHES EXPANSÍVEIS
        with st.expander("🔍 Ver detalhes completos"):
            # Progresso
            st.markdown("**📊 Progresso**")
            prog_col1, prog_col2, prog_col3 = st.columns(3)
            with prog_col1:
                st.metric("Aniversário", birthday)
            with prog_col2:
                st.metric("Abismo", abyss)
            with prog_col3:
                st.metric("Andar máx.", abyss_floor)

            # Exploração
            st.markdown("**🗺️ Exploração**")
            for key, label in MAP_AREAS:
                val = map_progress.get(key, 0)
                if val > 0:
                    color = "#7C3AED" if val >= 80 else "#0DCAF0" if val >= 50 else "#94A3B8"
                    st.progress(val / 100, text=f"{label} - {val}%")

            # Armas
            if weapons:
                st.markdown(f"**⚔️ Armas ({len(weapons)})**")
                for w in weapons[:6]:
                    wname = w.get("weapon_name", "?")
                    wchar = w.get("character_name", "-")
                    wref = w.get("refinement", "R1")
                    st.markdown(f"• **{wname}** ({wchar}) • {wref}")
                if len(weapons) > 6:
                    st.caption(f"+{len(weapons)-6} armas")

            # Observações
            if extra:
                st.markdown("**📝 Observações**")
                st.info(extra)

            # Timestamp
            st.caption(f"Atualizado em: {account.get('updated_at', '-')[:16]}")


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
    <div style="text-align: center; padding: 30px 20px; background: linear-gradient(180deg, rgba(124,58,237,0.15) 0%, transparent 100%); border-radius: 0 0 24px 24px; margin-bottom: 30px;">
        <h1 style="margin:0; color:#F8FAFC; font-size: 42px;">⚔️ Genshin Impact</h1>
        <p style="margin:10px 0 0 0; color:#94A3B8; font-size: 18px;">Contas disponíveis para venda • Atualizado em tempo real</p>
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

        st.divider()

        if st.button("🔄 Atualizar agora", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("""
        <div style="margin-top:30px; padding:16px; background:#1E293B; border-radius:12px; border:1px solid #334155;">
            <h4 style="color:#F8FAFC; margin:0 0 8px 0;">📞 Contato</h4>
            <p style="color:#94A3B8; font-size:13px; margin:0;">
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
            st.error("🔧 Configuração incompleta: SUPABASE_URL não definido nos Secrets.")
        st.markdown("""
        <div style="text-align:center; color:#64748B; font-size:12px; margin-top:40px; padding:20px;">
            Vitrine v2.0 • Genshin Account Manager Pro
        </div>
        """, unsafe_allow_html=True)
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
            blob = f"{acc.get('name','')} {acc.get('uid','')} {acc.get('tags','')}"
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

    # Stats
    total = len(filtered)
    total_5star = sum(len(parse_json_field(a, "characters_json")) for a in filtered)

    col1, col2, col3 = st.columns(3)
    col1.metric("Contas disponíveis", total)
    col2.metric("Total de personagens 5★", total_5star)
    col3.metric("Servidores", len(set(a.get("server") for a in filtered)))

    st.divider()

    # Grid de cards
    if not filtered:
        st.info("Nenhuma conta encontrada com os filtros selecionados.")
    else:
        for account in filtered:
            render_account_card(account)

    # Footer
    st.markdown(f"""
    <div style="text-align:center; color:#64748B; font-size:12px; margin-top:40px; padding:20px;">
        Vitrine v2.0 • Genshin Account Manager Pro • Última atualização: {datetime.now().strftime('%H:%M:%S')}<br>
        <span style="font-size:11px;">As informações são atualizadas automaticamente pelo vendedor.</span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
