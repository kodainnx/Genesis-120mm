# -*- coding: utf-8 -*-
"""
Calculadora de Tiro de Morteiro 120 mm - Versão Kivy Mobile (Android APK)
Desenvolvida para smartphones e tablets, com interface touch responsiva,
inspirada no sistema Gênesis (AMAN) e baseada nos manuais de tiro oficiais.
"""

import math
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.core.window import Window

# ==============================================================================
# BANCO DE DADOS INTEGRADO (TNT - TABELAS NUMÉRICAS DE TIRO)
# ==============================================================================
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
        1: { 1500: 981.5 },
        5: { 4000: 1090.9, 4500: 972.3 },
        6: { 5000: 1158.1, 5200: 890.8, 5300: 826.7, 5500: 1094.0, 6000: 1013.6, 6500: 886.4 },
        8: { 5500: 1161.9, 6000: 1104.7, 6500: 1035.3, 7000: 939.4 },
        9: { 6000: 1168.5, 6500: 1117.8 }
    }
}

# ==============================================================================
# LÓGICA MATEMÁTICA E CÁLCULO MILITAR
# ==============================================================================

def calcular_distancia_e_angulo(x_peca, y_peca, z_peca, x_alvo, y_alvo, z_alvo):
    dx = x_alvo - x_peca
    dy = y_alvo - y_peca
    desnivel = z_alvo - z_peca
    distancia = math.sqrt(dx**2 + dy**2)
    if dy != 0:
        radianos = math.atan2(dx, dy)
        mils = (radianos * 3200.0) / math.pi
        if mils < 0:
            mils += 6400.0
    else:
        mils = 1600.0 if dx > 0 else 4800.0
    return distancia, desnivel, mils

def calcular_sitio_topografico(alcance_m, desnivel_m, presumido_maior_que_100):
    alcance_km = alcance_m / 1000.0
    if alcance_km == 0:
        raise ValueError("Alcance não pode ser zero.")
    if presumido_maior_que_100:
        return desnivel_m / alcance_km
    else:
        return 1.02 * desnivel_m / alcance_km

def calcular_sitio_complementar(stio_topo_mils, fator_comp_si):
    # CComp_Si = -1.0 * Si_topo * fator [C-23-95 pág 5-17]
    return -1.0 * stio_topo_mils * fator_comp_si

def calcular_elevacao(ala_mils, stio_topo_mils, stio_comp_mils, tipo_tabela):
    tipo = tipo_tabela.upper()
    if tipo == 'CONV':
        return ala_mils - stio_topo_mils
    elif tipo == 'PR':
        si_total = stio_topo_mils + stio_comp_mils
        return ala_mils - si_total
    else:
        raise ValueError("tipo_tabela deve ser 'CONV' ou 'PR'.")

def interpolar_alca(tipo_tabela, carga, alcance_m):
    tipo = tipo_tabela.upper()
    if tipo not in TABELAS_TIRO or carga not in TABELAS_TIRO[tipo]:
        return None
    
    tabela = TABELAS_TIRO[tipo][carga]
    alcances = sorted(tabela.keys())
    
    if alcance_m in tabela:
        return tabela[alcance_m]
    
    if alcance_m < alcances[0] or alcance_m > alcances[-1]:
        return None
        
    for i in range(len(alcances) - 1):
        alc_inf = alcances[i]
        alc_sup = alcances[i+1]
        if alc_inf <= alcance_m <= alc_sup:
            alca_inf = tabela[alc_inf]
            alca_sup = tabela[alc_sup]
            alca = alca_inf + (alca_sup - alca_inf) * (alcance_m - alc_inf) / (alc_sup - alc_inf)
            return alca
    return None

def calcular_deriva_tiro(der_prch, der_aju, cder):
    corr_der = der_aju - der_prch
    der_tiro = der_prch + cder + corr_der
    return corr_der, der_tiro

def calcular_k_alc(corr_alc_m, alcance_prch_PD_m):
    alcance_km = alcance_prch_PD_m / 1000.0
    if alcance_km == 0:
        raise ValueError("Alcance não pode ser zero.")
    return corr_alc_m / alcance_km

def formatar_sitio_militar(valor):
    if valor > 0:
        return f"M {abs(valor):.2f}''' (Mais)"
    elif valor < 0:
        return f"m {abs(valor):.2f}''' (Menos)"
    else:
        return "0.00'''"

# ==============================================================================
# INTERFACE KIVY (MOBILE TOUCH)
# ==============================================================================

class GenesisM120Mobile(BoxLayout):
    def __init__(self, **kwargs):
        super(GenesisM120Mobile, self).__init__(orientation='vertical', **kwargs)
        
        # Variáveis compartilhadas
        self.mem_alcance = 4100.0
        self.mem_desnivel = -17.0
        self.mem_lancamento = 2854.0

        # Banner Superior
        header = Label(
            text="🎯 GÊNESIS-M120: CENTRAL DE TIRO",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height='50dp',
            color=(1, 1, 1, 1)
        )
        self.add_widget(header)

        # Painel de Abas
        self.tp = TabbedPanel(do_default_tab=False)
        self.add_widget(self.tp)

        # Abas
        self.tab_topo = TabbedPanelHeader(text="Topografia")
        self.tab_sitio = TabbedPanelHeader(text="Sítio/Elv")
        self.tab_deriva = TabbedPanelHeader(text="Deriva")
        self.tab_k = TabbedPanelHeader(text="Fator K")

        self.tp.add_widget(self.tab_topo)
        self.tp.add_widget(self.tab_sitio)
        self.tp.add_widget(self.tab_deriva)
        self.tp.add_widget(self.tab_k)

        # Construir conteúdo das abas
        self.tab_topo.content = self.build_topo_ui()
        self.tab_sitio.content = self.build_sitio_ui()
        self.tab_deriva.content = self.build_deriva_ui()
        self.tab_k.content = self.build_k_ui()

    def show_popup(self, titulo, mensagem):
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        popup_label = Label(text=mensagem, font_size='14sp')
        close_button = Button(text="Fechar", size_hint_y=None, height='45dp')
        layout.add_widget(popup_label)
        layout.add_widget(close_button)
        popup = Popup(title=titulo, content=layout, size_hint=(0.85, 0.4))
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    # --------------------------------------------------------------------------
    # ABA TOPOGRAFIA
    # --------------------------------------------------------------------------
    def build_topo_ui(self):
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing='10dp', padding='10dp', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text="📍 COORDENADAS DA PEÇA (LF)", bold=True, size_hint_y=None, height='30dp'))
        
        grid_p = GridLayout(cols=2, spacing='5dp', size_hint_y=None, height='110dp')
        grid_p.add_widget(Label(text="X Peça (m):"))
        self.txt_px = TextInput(text="43500.0", multiline=False)
        grid_p.add_widget(self.txt_px)
        grid_p.add_widget(Label(text="Y Peça (m):"))
        self.txt_py = TextInput(text="16900.0", multiline=False)
        grid_p.add_widget(self.txt_py)
        grid_p.add_widget(Label(text="Z Altura Peça (m):"))
        self.txt_pz = TextInput(text="300.0", multiline=False)
        grid_p.add_widget(self.txt_pz)
        layout.add_widget(grid_p)

        layout.add_widget(Label(text="🎯 COORDENADAS DO ALVO", bold=True, size_hint_y=None, height='30dp'))
        
        grid_a = GridLayout(cols=2, spacing='5dp', size_hint_y=None, height='110dp')
        grid_a.add_widget(Label(text="X Alvo (m):"))
        self.txt_ax = TextInput(text="40000.0", multiline=False)
        grid_a.add_widget(self.txt_ax)
        grid_a.add_widget(Label(text="Y Alvo (m):"))
        self.txt_ay = TextInput(text="19050.0", multiline=False)
        grid_a.add_widget(self.txt_ay)
        grid_a.add_widget(Label(text="Z Altura Alvo (m):"))
        self.txt_az = TextInput(text="283.0", multiline=False)
        grid_a.add_widget(self.txt_az)
        layout.add_widget(grid_a)

        btn_calc = Button(text="📊 Calcular Coordenadas", size_hint_y=None, height='50dp')
        btn_calc.bind(on_release=self.calc_topo)
        layout.add_widget(btn_calc)

        self.lbl_topo_res = Label(text="Distância: ---\nDesnível: ---\nLançamento: ---", font_size='15sp', size_hint_y=None, height='90dp')
        layout.add_widget(self.lbl_topo_res)

        btn_salvar = Button(text="💾 Aplicar no Cálculo de Sítio", size_hint_y=None, height='45dp')
        btn_salvar.bind(on_release=self.salvar_topo)
        layout.add_widget(btn_salvar)

        scroll.add_widget(layout)
        return scroll

    def calc_topo(self, instance):
        try:
            px, py, pz = float(self.txt_px.text), float(self.txt_py.text), float(self.txt_pz.text)
            ax, ay, az = float(self.txt_ax.text), float(self.txt_ay.text), float(self.txt_az.text)
            
            dist, desnivel, lanc = calcular_distancia_e_angulo(px, py, pz, ax, ay, az)
            self.mem_alcance = dist
            self.mem_desnivel = desnivel
            self.mem_lancamento = lanc

            txt = f"Distância: {dist:.2f} m\nDesnível: {desnivel:.2f} m\nLançamento: {lanc:.2f}'''"
            self.lbl_topo_res.text = txt
        except ValueError:
            self.show_popup("Erro", "Insira coordenadas numéricas válidas.")

    def salvar_topo(self, instance):
        self.txt_sitio_alcance.text = f"{self.mem_alcance:.2f}"
        self.txt_sitio_desnivel.text = f"{self.mem_desnivel:.2f}"
        self.show_popup("Sucesso", "Dados transferidos para a aba Sítio/Elevação!")

    # --------------------------------------------------------------------------
    # ABA SÍTIO E ELEVAÇÃO
    # --------------------------------------------------------------------------
    def build_sitio_ui(self):
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing='8dp', padding='10dp', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text="⛰️ CÁLCULO DE SÍTIO E ELEVAÇÃO", bold=True, size_hint_y=None, height='30dp'))

        grid = GridLayout(cols=2, spacing='5dp', size_hint_y=None, height='180dp')
        grid.add_widget(Label(text="Alcance (m):"))
        self.txt_sitio_alcance = TextInput(text="4100.0", multiline=False)
        grid.add_widget(self.txt_sitio_alcance)

        grid.add_widget(Label(text="Desnível (m):"))
        self.txt_sitio_desnivel = TextInput(text="-17.0", multiline=False)
        grid.add_widget(self.txt_sitio_desnivel)

        grid.add_widget(Label(text="Munição:"))
        self.spn_mun = Spinner(text="PR", values=["CONV", "PR"])
        self.spn_mun.bind(text=self.on_mun_change)
        grid.add_widget(self.spn_mun)

        grid.add_widget(Label(text="Carga:"))
        self.spn_carga = Spinner(text="8", values=["1", "5", "6", "8", "9"])
        grid.add_widget(self.spn_carga)

        grid.add_widget(Label(text="Fator CComp (PR):"))
        self.txt_fator = TextInput(text="0.13", multiline=False)
        grid.add_widget(self.txt_fator)

        layout.add_widget(grid)

        # Checkboxes
        box_chk1 = BoxLayout(orientation='horizontal', size_hint_y=None, height='35dp')
        self.chk_auto = CheckBox(active=True)
        box_chk1.add_widget(self.chk_auto)
        box_chk1.add_widget(Label(text="Interpolar Alça Auto (TNT)"))
        layout.add_widget(box_chk1)

        grid_alca = GridLayout(cols=2, spacing='5dp', size_hint_y=None, height='40dp')
        grid_alca.add_widget(Label(text="Alça Manual (mils):"))
        self.txt_alca_manual = TextInput(text="1019.0", multiline=False)
        grid_alca.add_widget(self.txt_alca_manual)
        layout.add_widget(grid_alca)

        btn_calc = Button(text="🧮 Processar Tiro", size_hint_y=None, height='50dp')
        btn_calc.bind(on_release=self.calc_sitio)
        layout.add_widget(btn_calc)

        self.lbl_sitio_res = Label(
            text="Si Topo: ---\nSi Comp: ---\nSi Tot: ---\nAlça: ---\nELEVAÇÃO: ---",
            font_size='15sp',
            bold=True,
            size_hint_y=None,
            height='120dp'
        )
        layout.add_widget(self.lbl_sitio_res)

        scroll.add_widget(layout)
        return scroll

    def on_mun_change(self, spinner, text):
        if text == "CONV":
            self.spn_carga.values = ["1", "2", "3", "4", "7"]
            self.spn_carga.text = "4"
        else:
            self.spn_carga.values = ["1", "5", "6", "8", "9"]
            self.spn_carga.text = "8"

    def calc_sitio(self, instance):
        try:
            alc = float(self.txt_sitio_alcance.text)
            desn = float(self.txt_sitio_desnivel.text)
            mun = self.spn_mun.text
            
            if self.chk_auto.active:
                carga = int(self.spn_carga.text)
                alca = interpolar_alca(mun, carga, alc)
                if alca is None:
                    self.show_popup("Aviso", "Alcance fora da tabela de tiro. Desmarque busca auto e use alça manual.")
                    return
            else:
                alca = float(self.txt_alca_manual.text)

            si_topo = calcular_sitio_topografico(alc, desn, False)
            si_comp = 0.0
            if mun == "PR":
                fator = float(self.txt_fator.text)
                si_comp = calcular_sitio_complementar(si_topo, fator)
            
            si_tot = si_topo + si_comp
            elv = calcular_elevacao(alca, si_topo, si_comp, mun)

            txt = (
                f"Si Topo: {formatar_sitio_militar(si_topo)}\n"
                f"Si Comp: {formatar_sitio_militar(si_comp)}\n"
                f"Si Tot: {formatar_sitio_militar(si_tot)}\n"
                f"Alça Utilizada: {alca:.2f}'''\n"
                f"ELEVAÇÃO FINAL: {elv:.1f}'''"
            )
            self.lbl_sitio_res.text = txt
        except ValueError:
            self.show_popup("Erro", "Verifique os números digitados.")

    # --------------------------------------------------------------------------
    # ABA DERIVA
    # --------------------------------------------------------------------------
    def build_deriva_ui(self):
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing='10dp', padding='10dp', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text="🧭 DERIVA DE TIRO (DEPURAÇÃO)", bold=True, size_hint_y=None, height='30dp'))

        grid = GridLayout(cols=2, spacing='5dp', size_hint_y=None, height='110dp')
        grid.add_widget(Label(text="Deriva Prancheta (mils):"))
        self.txt_der_prch = TextInput(text="2854.0", multiline=False)
        grid.add_widget(self.txt_der_prch)

        grid.add_widget(Label(text="Deriva Ajustada (mils):"))
        self.txt_der_aju = TextInput(text="2854.0", multiline=False)
        grid.add_widget(self.txt_der_aju)

        grid.add_widget(Label(text="Contraderivação (mils):"))
        self.txt_cder = TextInput(text="0.0", multiline=False)
        grid.add_widget(self.txt_cder)

        layout.add_widget(grid)

        btn = Button(text="🧭 Calcular Deriva", size_hint_y=None, height='50dp')
        btn.bind(on_release=self.calc_deriva)
        layout.add_widget(btn)

        self.lbl_der_res = Label(text="Correção Deriva: ---\nDERIVA DE TIRO: ---", font_size='15sp', bold=True, size_hint_y=None, height='70dp')
        layout.add_widget(self.lbl_der_res)

        scroll.add_widget(layout)
        return scroll

    def calc_deriva(self, instance):
        try:
            dp = float(self.txt_der_prch.text)
            da = float(self.txt_der_aju.text)
            cd = float(self.txt_cder.text)
            corr, dt = calcular_deriva_tiro(dp, da, cd)
            self.lbl_der_res.text = f"Correção Deriva: {corr:+.1f} mils\nDERIVA DE TIRO: {dt:.1f}'''"
        except ValueError:
            self.show_popup("Erro", "Valores de deriva inválidos.")

    # --------------------------------------------------------------------------
    # ABA FATOR K
    # --------------------------------------------------------------------------
    def build_k_ui(self):
        scroll = ScrollView()
        layout = GridLayout(cols=1, spacing='10dp', padding='10dp', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text="📈 FATOR K EM ALCANCE", bold=True, size_hint_y=None, height='30dp'))

        grid = GridLayout(cols=2, spacing='5dp', size_hint_y=None, height='75dp')
        grid.add_widget(Label(text="Correção Alcance PD (m):"))
        self.txt_k_corr = TextInput(text="0.0", multiline=False)
        grid.add_widget(self.txt_k_corr)

        grid.add_widget(Label(text="Alcance Prancheta PD (m):"))
        self.txt_k_alc = TextInput(text="4100.0", multiline=False)
        grid.add_widget(self.txt_k_alc)

        layout.add_widget(grid)

        btn = Button(text="📈 Determinar K", size_hint_y=None, height='50dp')
        btn.bind(on_release=self.calc_k)
        layout.add_widget(btn)

        self.lbl_k_res = Label(text="Fator K: ---\nFórmula: Corr_alc = K * Alc_km", font_size='14sp', size_hint_y=None, height='70dp')
        layout.add_widget(self.lbl_k_res)

        scroll.add_widget(layout)
        return scroll

    def calc_k(self, instance):
        try:
            corr = float(self.txt_k_corr.text)
            alc = float(self.txt_k_alc.text)
            k = calcular_k_alc(corr, alc)
            self.lbl_k_res.text = f"Fator K: {k:+.2f} m/km\nAplica-se: Corr_alc = {k:.2f} * Alcance_km"
        except ValueError:
            self.show_popup("Erro", "Valores numéricos inválidos.")

class GenesisApp(App):
    def build(self):
        self.title = "Gênesis-M120 Mobile"
        return GenesisM120Mobile()

if __name__ == '__main__':
    GenesisApp().run()
