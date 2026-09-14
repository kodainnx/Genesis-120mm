import streamlit as st
import math
from dataclasses import dataclass

# Configuração de Página
st.set_page_config(
    page_title="Calculadora de Tiro 120 mm",
    page_icon="🎯",
    layout="centered",
)

# Banco de Dados das Tabelas Numéricas de Tiro (TNT) do Morteiro 120mm M2 Raiado
# Dados extraídos dos manuais oficiais (C-23-95 e Cadernetas de Operações da AMAN)
TABELAS_TIRO = {
    "CONV": {
        1: {
            800: 1402.0, 850: 1388.0, 900: 1375.0, 950: 1361.0, 1000: 1348.0, 1050: 1334.0,
            1100: 1319.0, 1150: 1305.0, 1200: 1290.0, 1250: 1275.0, 1300: 1259.0,
            1350: 1243.0, 1400: 1227.0, 1450: 1210.0, 1500: 1193.0, 1550: 1175.0, 1600: 1156.0
        },
        2: {
            1900: 1210.0, 1950: 1197.0, 2000: 1184.0, 2050: 1169.0, 2100: 1155.0,
            2150: 1140.0, 2200: 1124.0, 2250: 1108.0, 2300: 1091.0, 2350: 1073.0,
            2400: 1055.0, 2450: 1034.0, 2500: 1013.0, 2550: 989.0, 2600: 962.0,
            2650: 932.0, 2700: 893.0, 2750: 835.0, 2765: 800.0
        },
        3: {
            2200: 1238.0, 2250: 1228.0, 2300: 1217.0, 2350: 1206.0, 2400: 1195.0,
            2450: 1184.0, 2500: 1173.0, 2550: 1161.0, 2600: 1149.0, 2650: 1136.0,
            2700: 1123.0, 2750: 1110.0, 2800: 1096.0, 2850: 1082.0, 2900: 1067.0,
            2950: 1051.0, 3500: 1291.0, 4000: 1237.0
        },
        4: {
            3545: 1141.0, 4050: 1032.0, 4100: 1019.0
        },
        7: {
            4000: 1264.0, 4050: 1259.0, 4100: 1254.0, 4150: 1248.0, 4200: 1243.0,
            4250: 1238.0, 4300: 1232.0, 4350: 1227.0, 4400: 1221.0, 4450: 1216.0,
            4500: 1210.0, 4550: 1204.0, 4600: 1199.0, 4650: 1193.0, 4700: 1187.0,
            4750: 1181.0, 4800: 1175.0, 4850: 1169.0, 4900: 1163.0, 4950: 1156.0,
            5000: 1150.0, 5250: 1116.0, 5300: 1109.0, 5350: 1102.0, 5400: 1094.0,
            5450: 1086.0, 5500: 1079.0, 5550: 1071.0, 5600: 1063.0, 5650: 1054.0,
            5700: 1045.0, 5750: 1037.0, 6350: 886.0, 6400: 864.0, 6450: 834.0, 6486: 800.0
        }
    },
    "PR": {
        1: {
            1500: 981.5
        },
        5: {
            4000: 1090.9, 4500: 972.3
        },
        6: {
            5000: 1158.1, 5200: 890.8, 5300: 826.7, 5500: 1094.0, 6000: 1013.6, 6500: 886.4
        },
        8: {
            5500: 1161.9, 6000: 1104.7, 6500: 1035.3, 7000: 939.4
        },
        9: {
            6000: 1168.5, 6500: 1117.8
        }
    }
}

### ==== MODELOS DE DADOS ====
@dataclass
class TiroInput:
    alcance_prancheta_m: float
    desnivel_m: float
    ala_mils: float
    tipo_tabela: str
    stio_presumido_maior_que_100: bool = False
    fator_comp_si: float = 0.0

@dataclass
class TiroOutput:
    stio_topografico_mils: float
    stio_complementar_mils: float
    stio_total_mils: float
    elevacao_mils: float

### ==== FUNÇÕES DE CÁLCULO ====
def calcular_stio_topografico(alcance_m: float, desnivel_m: float, presumido_maior_que_100: bool) -> float:
    """Calcula o sítio topográfico usando as fórmulas oficiais do manual."""
    alcance_km = alcance_m / 1000.0
    if alcance_km == 0:
        raise ValueError("Alcance não pode ser zero.")
    if presumido_maior_que_100:
        s_mils = desnivel_m / alcance_km
    else:
        s_mils = 1.02 * desnivel_m / alcance_km
    return s_mils

def calcular_stio_complementar(stio_topo_mils: float, fator_comp_si: float) -> float:
    """Correção complementar de sítio: CComp_Si = -1.0 * Si_topo * fator.
    A correção complementar é negativa quando o alvo está acima da peça (sítio > 0)
    e positiva quando se encontra abaixo (sítio < 0) [C-23-95 pág 5-17].
    """
    return -1.0 * stio_topo_mils * fator_comp_si

def calcular_elevacao(ala_mils: float, stio_topo_mils: float, stio_comp_mils: float, tipo_tabela: str) -> float:
    """Calcula a elevação conforme o tipo de tiro e munição.
    CONV (Munição Convencional): Elv = Ala - Si_topo
    PR (Munição Pré-Raiada):      Elv = Ala - Si_total (onde Si_total = Si_topo + CComp_Si)
    """
    tipo = tipo_tabela.upper()
    if tipo == 'CONV':
        return ala_mils - stio_topo_mils
    elif tipo == 'PR':
        si_total = stio_topo_mils + stio_comp_mils
        return ala_mils - si_total
    else:
        raise ValueError("tipo_tabela deve ser 'CONV' ou 'PR'.")

def processar_tiro(dados: TiroInput) -> TiroOutput:
    """Executa todos os cálculos de sítio e elevação."""
    si_topo = calcular_stio_topografico(
        dados.alcance_prancheta_m,
        dados.desnivel_m,
        dados.stio_presumido_maior_que_100,
    )
    ccomp_si = calcular_stio_complementar(si_topo, dados.fator_comp_si)
    si_total = si_topo + ccomp_si
    elv = calcular_elevacao(dados.ala_mils, si_topo, ccomp_si, dados.tipo_tabela)
    return TiroOutput(
        stio_topografico_mils=si_topo,
        stio_complementar_mils=ccomp_si,
        stio_total_mils=si_total,
        elevacao_mils=elv,
    )

def calcular_deriva_tiro(deriva_prancheta_mils: float, deriva_ajustada_mils: float, contraderivacao_mils: float):
    """Calcula correção de deriva e deriva de tiro final.
    CorrDer = Der_Aju_CPel - Der_Prch_CPel
    Der_Tiro = Der_Prch + CDer + CorrDer
    """
    corr_der = deriva_ajustada_mils - deriva_prancheta_mils
    der_tiro = deriva_prancheta_mils + contraderivacao_mils + corr_der
    return corr_der, der_tiro

def calcular_k_alc(corr_alc_m: float, alcance_prch_PD_m: float) -> float:
    """Calcula K em alcance: K_Alc = Corr_Alc (m) / Alc_Prch_PD (km)."""
    alcance_km = alcance_prch_PD_m / 1000.0
    if alcance_km == 0:
        raise ValueError("Alcance da PD não pode ser zero.")
    return corr_alc_m / alcance_km

def interpolar_alca(tipo_tabela: str, carga: int, alcance_m: float) -> float:
    """Retorna a alça interpolada para o alcance fornecido usando a base de dados."""
    tipo = tipo_tabela.upper()
    if tipo not in TABELAS_TIRO or carga not in TABELAS_TIRO[tipo]:
        return None
    
    tabela = TABELAS_TIRO[tipo][carga]
    alcances = sorted(tabela.keys())
    
    if alcance_m in tabela:
        return tabela[alcance_m]
    
    # Validação de limites
    if alcance_m < alcances[0] or alcance_m > alcances[-1]:
        return None
        
    for i in range(len(alcances) - 1):
        alc_inf = alcances[i]
        alc_sup = alcances[i+1]
        if alc_inf < alcance_m < alc_sup:
            alca_inf = tabela[alc_inf]
            alca_sup = tabela[alc_sup]
            # Interpolação linear exata do manual [C-23-95 pág 5-16]
            alca = alca_inf + (alca_sup - alca_inf) * (alcance_m - alc_inf) / (alc_sup - alc_inf)
            return alca
            
    return None

def formatar_sitio_militar(valor: float) -> str:
    """Formata o sítio seguindo as convenções e notações militares do manual C-23-95."""
    if valor > 0:
        return f"M{abs(valor):.1f}''' (Mais)"
    elif valor < 0:
        return f"m{abs(valor):.1f}''' (Menos)"
    else:
        return "0.00'''"

### ==== INICIALIZAÇÃO DE ESTADO ====
if "coordenadas_calculadas" not in st.session_state:
    st.session_state["coordenadas_calculadas"] = False
    st.session_state["dist_pranch"] = 4100.0
    st.session_state["desnivel"] = -17.0
    st.session_state["lançamento"] = 2854.0

### ==== INTERFACE STREAMLIT ====
st.title("🎯 Gênesis-M120: Central de Tiro de Morteiro 120 mm")
st.markdown(
    """Aplicação web integrada para apoio ao cálculo de tiro tático do **Morteiro Pesado 120 mm M2 raiado**.
    Inspirada no sistema **Gênesis**, esta ferramenta automatiza trabalhos topográficos e de Central de Tiro (C Tir)."""
)

# Abas Principais
aba_coord, aba_sitio, aba_deriva, aba_k = st.tabs([
    "📍 Coordenadas e Topografia",
    "⛰️ Sítio + Elevação",
    "↩️ Deriva de Tiro",
    "📈 K em Alcance",
])

### --- Aba 1: Coordenadas e Topografia ---
with aba_coord:
    st.subheader("Cálculos Topográficos da Central de Tiro (C Tir)")
    st.markdown(
        """Determine instantaneamente a distância de prancheta, o desnível e o lançamento de tiro (azimute) 
        a partir das coordenadas da Linha de Fogo (Peça) e do Alvo."""
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Peça (Morteiro / Linha de Fogo)**")
        px = st.number_input("Easting / X (m)", value=10000.0, step=100.0, key="px")
        py = st.number_input("Northing / Y (m)", value=10000.0, step=100.0, key="py")
        pz = st.number_input("Altitude / Z (m)", value=400.0, step=10.0, key="pz")
        
    with col2:
        st.markdown("**Alvo / Ponto de Impacto**")
        # Valor default gera aprox 4000m e -17m desnivel
        ax = st.number_input("Easting / X (m)", value=12828.0, step=100.0, key="ax")
        ay = st.number_input("Northing / Y (m)", value=12828.0, step=100.0, key="ay")
        az = st.number_input("Altitude / Z (m)", value=383.0, step=10.0, key="az")
        
    if st.button("Calcular Dados de Prancheta", key="btn_coord"):
        dx = ax - px
        dy = ay - py
        distancia = math.sqrt(dx**2 + dy**2)
        desnivel = az - pz
        
        # Calcular ângulo do lançamento em milésimos (6400''')
        # tg Â = dx / dy -> atan2(dx, dy) fornece o azimute no sentido horário a partir de Y+
        angle_rad = math.atan2(dx, dy)
        if angle_rad < 0:
            angle_rad += 2 * math.pi
        angulo_mils = angle_rad * (6400.0 / (2 * math.pi))
        
        st.session_state["dist_pranch"] = round(distancia, 1)
        st.session_state["desnivel"] = round(desnivel, 1)
        st.session_state["lançamento"] = round(angulo_mils, 1)
        st.session_state["coordenadas_calculadas"] = True
        
        st.success("Trabalho topográfico concluído com sucesso!")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Distância (m)", f"{distancia:.1f} m")
        c2.metric("Desnível (m)", f"{desnivel:.1f} m")
        c3.metric("Lançamento (mils)", f"{angulo_mils:.1f}'''")
        
        st.info("💡 Clique na aba **Sítio + Elevação** para calcular a elevação de tiro. Os dados acima já foram enviados automaticamente para as outras abas!")

### --- Aba 2: Sítio + Elevação ---
with aba_sitio:
    st.subheader("Cálculo de Sítio e Elevação de Tiro")
    
    if st.session_state["coordenadas_calculadas"]:
        st.info(f"📋 Dados importados da topografia: **Alcance = {st.session_state['dist_pranch']:.1f} m** | **Desnível = {st.session_state['desnivel']:.1f} m**")
    
    col1, col2 = st.columns(2)
    with col1:
        alcance = st.number_input(
            "Alcance de prancheta (m)", 
            min_value=0.0, 
            step=50.0, 
            value=float(st.session_state["dist_pranch"]),
            help="Distância horizontal morteiro–alvo na prancheta de tiro."
        )
        desnivel = st.number_input(
            "Desnível (alt alvo - alt morteiro) em m",
            step=1.0,
            value=float(st.session_state["desnivel"]),
            help="Positivo se o alvo está acima da peça, negativo se abaixo."
        )
        tipo = st.selectbox(
            "Tipo de munição / Tabela",
            ["CONV", "PR"],
            help="CONV para munição explosiva convencional, PR para munição pré-raiada de 120 mm."
        )
        
    with col2:
        # Limitar as cargas com base no tipo
        if tipo == "CONV":
            carga = st.selectbox("Carga de projeção", [1, 2, 3, 4, 7], help="Cargas disponíveis nos manuais para Tiro Convencional.")
        else:
            carga = st.selectbox("Carga de projeção", [1, 5, 6, 8, 9], help="Cargas disponíveis nos manuais para Tiro Pré-Raiado.")
            
        auto_alca = st.checkbox("Interpolar Alça Automaticamente", value=True, help="Usa os dados das Tabelas Numéricas de Tiro (TNT) oficiais contidas nos manuais para interpolar a alça de tiro exata.")
        
        if auto_alca:
            alca_auto = interpolar_alca(tipo, carga, alcance)
            if alca_auto is not None:
                st.write(f"Alça Interpolada (Tabela): **{alca_auto:.1f} mils**")
                ala = alca_auto
            else:
                st.warning("Alcance ou Carga fora da cobertura das tabelas parciais. Insira a alça manualmente abaixo.")
                ala = st.number_input(
                    "Alça de tiro (mils) [Manual]", 
                    min_value=0.0, 
                    step=1.0, 
                    value=1019.0,
                    help="Insira a alça lida ou aproximada das Tabelas Numéricas de Tiro (TNT)."
                )
        else:
            ala = st.number_input(
                "Alça de tiro (mils) [Manual]", 
                min_value=0.0, 
                step=1.0, 
                value=1019.0,
                help="Insira a alça lida na tabela de tiro (TNT) para o alcance e carga selecionados."
            )

    maior_que_100 = st.checkbox(
        "Sítio topográfico presumido maior que 100 milésimos",
        value=False,
        help="Marque se espera sítios muito íngremes; caso contrário, utiliza a fórmula S = 1,02 * desnível / alcance_km."
    )

    fator_comp_si = 0.0
    if tipo == "PR":
        fator_comp_si = st.number_input(
            "Fator de correção complementar de sítio (Tab C)",
            step=0.01,
            value=0.0,
            help="Fator de ângulo complementar de sítio lido na Tab C para o alcance correspondente."
        )

    # Validar Alcance máximo com base na Munição
    limite_mrt = 6500.0 if tipo == "CONV" else 8000.0
    if alcance > limite_mrt:
        st.warning(f"⚠️ Atenção: O alcance de prancheta ({alcance:.0f} m) excede o alcance máximo homologado para a munição selecionada ({limite_mrt:.0f} m)!")

    if st.button("Calcular Sítio e Elevação", key="btn_sitio"):
        try:
            dados = TiroInput(
                alcance_prancheta_m=alcance,
                desnivel_m=desnivel,
                ala_mils=ala,
                tipo_tabela=tipo,
                stio_presumido_maior_que_100=maior_que_100,
                fator_comp_si=fator_comp_si,
            )
            resultado = processar_tiro(dados)
            st.success("Cálculos de Sítio e Elevação realizados com sucesso!")
            
            st.markdown("### Resultados")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.write(f"Sítio topográfico: **{formatar_sitio_militar(resultado.stio_topografico_mils)}**")
                st.write(f"Sítio complementar: **{formatar_sitio_militar(resultado.stio_complementar_mils)}**")
            with col_r2:
                st.write(f"Sítio total final: **{formatar_sitio_militar(resultado.stio_total_mils)}**")
                st.write(f"**Elevação final do Tubo: {resultado.elevacao_mils:.1f} milésimos** 🎯")
        except ValueError as e:
            st.error(f"Erro nos cálculos: {e}")

### --- Aba 3: Deriva de Tiro ---
with aba_deriva:
    st.subheader("Cálculo de Deriva de Tiro e Depuração")
    st.markdown(
        """Determine a deriva de tiro aplicando a contraderivação (Tab A) 
        referente à derivação lateral inerente do raiamento do morteiro."""
    )
    
    if st.session_state["coordenadas_calculadas"]:
        st.info(f"📋 Lançamento importado da topografia: **{st.session_state['lançamento']:.1f} mils**")
        default_der_prch = float(st.session_state["lançamento"])
    else:
        default_der_prch = 2854.0
        
    col1, col2 = st.columns(2)
    with col1:
        der_prch = st.number_input(
            "Deriva de prancheta do C Pel (mils)",
            step=1.0,
            value=default_der_prch,
            help="Deriva obtida na prancheta de tiro referente ao centro do pelotão."
        )
        der_aju = st.number_input(
            "Deriva ajustada do C Pel (mils)",
            step=1.0,
            value=default_der_prch,
            help="Deriva lida após a regulação prática de tiro (elemento ajustado)."
        )
    with col2:
        cder = st.number_input(
            "Contraderivação (mils - Tab A)",
            step=1.0,
            value=0.0,
            help="Correção lida na Tab A para compensar a derivação lateral causada pelo raiamento à direita."
        )

    if st.button("Calcular Deriva de Tiro", key="btn_deriva"):
        corr_der, der_tiro = calcular_deriva_tiro(der_prch, der_aju, cder)
        st.success("Cálculo realizado!")
        st.markdown("### Resultados")
        st.write(f"Correção de deriva (mils): **{corr_der:.1f} mils**")
        st.write(f"**Deriva de tiro final: {der_tiro:.1f} mils** 🎯")

### --- Aba 4: K em Alcance ---
with aba_k:
    st.subheader("Cálculo de K em Alcance (Regulação)")
    st.markdown(
        """Determine o fator **K em alcance** de forma científica a partir de uma regulação prática 
        em um Alvo Auxiliar (ou Ponto de Regulação)."""
    )
    
    col1, col2 = st.columns(2)
    with col1:
        corr_alc = st.number_input(
            "Correção em alcance (m)",
            step=10.0,
            value=0.0,
            help="Diferença entre o alcance ajustado (ala ajustada) e o alcance de prancheta da PD."
        )
    with col2:
        alc_prch_PD = st.number_input(
            "Alcance de prancheta da PD para o alvo auxiliar (m)",
            step=10.0,
            value=4100.0,
            help="Alcance de prancheta lido para a Peça Diretriz no alvo auxiliar."
        )

    if st.button("Calcular Fator K", key="btn_k"):
        try:
            k_alc = calcular_k_alc(corr_alc, alc_prch_PD)
            st.success("Fator K calculado!")
            st.markdown("### Resultado")
            st.write(f"K em alcance: **{k_alc:.2f} m/km**")
            st.markdown(
                f"""Alique esse fator para outros alvos na mesma zona:
                `Correção_alc (m) = {k_alc:.2f} * Alcance_prancheta_alvo (km)`."""
            )
        except ValueError as e:
            st.error(f"Erro no cálculo: {e}")
