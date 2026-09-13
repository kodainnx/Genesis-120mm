
import os
import sys

print("🚀 Iniciando processo de compilação do APK do Morteiro 120 mm...")

# Configurar variáveis de ambiente necessárias no Colab
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"

# 1. Instalar dependências do sistema e versão compatível do Cython (< 3.0.0)
print("\n📦 [1/5] Instalando dependências do sistema e Cython compatível...")
os.system("pip uninstall -y cython")
os.system("pip install 'cython<3.0.0' buildozer kivy")
os.system("sudo apt-get update")
os.system("sudo apt-get install -y build-essential git python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev openjdk-17-jdk unzip cmake lld ninja-build autoconf libtool pkg-config libffi-dev libssl-dev")

# 2. Criar o arquivo main.py (Código Kivy do Morteiro 120mm)
print("\n📝 [2/5] Escrevendo arquivo main.py...")
kivy_code = """# -*- coding: utf-8 -*-
import math
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader

TABELAS_TIRO = {
    "CONV": {
        1: {800: 1402.0, 900: 1375.0, 1000: 1348.0, 1100: 1319.0, 1200: 1290.0, 1300: 1259.0, 1400: 1227.0, 1500: 1193.0, 1600: 1156.0},
        2: {1900: 1210.0, 2000: 1184.0, 2100: 1155.0, 2200: 1124.0, 2300: 1091.0, 2400: 1055.0, 2500: 1013.0, 2600: 962.0, 2700: 893.0},
        3: {2200: 1238.0, 2300: 1217.0, 2400: 1195.0, 2500: 1173.0, 2600: 1149.0, 2700: 1123.0, 2800: 1096.0, 2900: 1067.0},
        4: {3545: 1141.0, 4050: 1032.0, 4100: 1019.0},
        7: {4000: 1264.0, 4200: 1243.0, 4400: 1221.0, 4600: 1199.0, 4800: 1175.0, 5000: 1150.0, 5500: 1079.0, 6000: 1063.0, 6486: 800.0}
    },
    "PR": {
        1: {1500: 981.5},
        5: {4000: 1090.9, 4500: 972.3},
        6: {5000: 1158.1, 5200: 890.8, 5500: 1094.0, 6000: 1013.6, 6500: 886.4},
        8: {5500: 1161.9, 6000: 1104.7, 6500: 1035.3, 7000: 939.4},
        9: {6000: 1168.5, 6500: 1117.8}
    }
}

def calc_topo(px, py, pz, ax, ay, az):
    dx = ax - px
    dy = ay - py
    desn = az - pz
    dist = math.sqrt(dx**2 + dy**2)
    mils = 1600.0 if dx > 0 else 4800.0
    if dy != 0:
        rad = math.atan2(dx, dy)
        mils = (rad * 3200.0) / math.pi
        if mils < 0: mils += 6400.0
    return dist, desn, mils

def interp_alca(mun, carga, alc):
    if mun not in TABELAS_TIRO or carga not in TABELAS_TIRO[mun]: return None
    tab = TABELAS_TIRO[mun][carga]
    alcs = sorted(tab.keys())
    if alc in tab: return tab[alc]
    if alc < alcs[0] or alc > alcs[-1]: return None
    for i in range(len(alcs)-1):
        if alcs[i] <= alc <= alcs[i+1]:
            a1, a2 = tab[alcs[i]], tab[alcs[i+1]]
            return a1 + (a2 - a1)*(alc - alcs[i])/(alcs[i+1] - alcs[i])
    return None

class Calc120App(App):
    def build(self):
        self.title = "Central de Tiro Morteiro 120 mm"
        panel = TabbedPanel(do_default_tab=False)
        
        # Aba Topografia
        th1 = TabbedPanelHeader(text="Topografia")
        box1 = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box1.add_widget(Label(text="[COORDENADAS PEÇA / ALVO]", font_size='18sp', bold=True, size_hint_y=None, height=40))
        
        grid_p = GridLayout(cols=3, size_hint_y=None, height=100)
        grid_p.add_widget(Label(text="Penta X:"))
        self.in_px = TextInput(text="43500", multiline=False)
        grid_p.add_widget(self.in_px)
        grid_p.add_widget(Label(text="Penta Y:"))
        self.in_py = TextInput(text="16900", multiline=False)
        grid_p.add_widget(self.in_py)
        grid_p.add_widget(Label(text="Penta Z:"))
        self.in_pz = TextInput(text="300", multiline=False)
        grid_p.add_widget(self.in_pz)
        box1.add_widget(grid_p)
        
        grid_a = GridLayout(cols=3, size_hint_y=None, height=100)
        grid_a.add_widget(Label(text="Alvo X:"))
        self.in_ax = TextInput(text="40000", multiline=False)
        grid_a.add_widget(self.in_ax)
        grid_a.add_widget(Label(text="Alvo Y:"))
        self.in_ay = TextInput(text="19050", multiline=False)
        grid_a.add_widget(self.in_ay)
        grid_a.add_widget(Label(text="Alvo Z:"))
        self.in_az = TextInput(text="283", multiline=False)
        grid_a.add_widget(self.in_az)
        box1.add_widget(grid_a)
        
        btn_c1 = Button(text="Calcular Coordenadas", size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.2, 1))
        btn_c1.bind(on_press=self.do_calc_topo)
        box1.add_widget(btn_c1)
        
        self.lbl_r1 = Label(text="Distância: ---\nDesnível: ---\nLançamento: ---", font_size='16sp')
        box1.add_widget(self.lbl_r1)
        th1.content = box1
        panel.add_widget(th1)
        
        # Aba Sítio
        th2 = TabbedPanelHeader(text="Sítio e Elevação")
        box2 = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box2.add_widget(Label(text="[CÁLCULO DE SÍTIO E ELEVAÇÃO]", font_size='18sp', bold=True, size_hint_y=None, height=40))
        
        grid_s = GridLayout(cols=2, size_hint_y=None, height=120)
        grid_s.add_widget(Label(text="Alcance (m):"))
        self.in_alc = TextInput(text="4100", multiline=False)
        grid_s.add_widget(self.in_alc)
        grid_s.add_widget(Label(text="Desnível (m):"))
        self.in_desn = TextInput(text="-17", multiline=False)
        grid_s.add_widget(self.in_desn)
        grid_s.add_widget(Label(text="Munição (CONV/PR):"))
        self.in_mun = TextInput(text="PR", multiline=False)
        grid_s.add_widget(self.in_mun)
        grid_s.add_widget(Label(text="Carga:"))
        self.in_cg = TextInput(text="8", multiline=False)
        grid_s.add_widget(self.in_cg)
        box2.add_widget(grid_s)
        
        btn_c2 = Button(text="Calcular Elevação", size_hint_y=None, height=50, background_color=(0.8, 0.2, 0.2, 1))
        btn_c2.bind(on_press=self.do_calc_sitio)
        box2.add_widget(btn_c2)
        
        self.lbl_r2 = Label(text="Si Topo: ---\nSi Total: ---\nAlça: ---\nElevação: ---", font_size='16sp')
        box2.add_widget(self.lbl_r2)
        th2.content = box2
        panel.add_widget(th2)
        
        return panel

    def do_calc_topo(self, instance):
        try:
            px, py, pz = float(self.in_px.text), float(self.in_py.text), float(self.in_pz.text)
            ax, ay, az = float(self.in_ax.text), float(self.in_ay.text), float(self.in_az.text)
            dist, desn, lanc = calc_topo(px, py, pz, ax, ay, az)
            self.lbl_r1.text = f"Distância: {dist:.2f} m\nDesnível: {desn:.2f} m\nLançamento: {lanc:.2f} mils"
            self.in_alc.text = f"{dist:.2f}"
            self.in_desn.text = f"{desn:.2f}"
        except Exception as e:
            self.lbl_r1.text = f"Erro: {e}"

    def do_calc_sitio(self, instance):
        try:
            alc = float(self.in_alc.text)
            desn = float(self.in_desn.text)
            mun = self.in_mun.text.strip().upper()
            cg = int(self.in_cg.text)
            
            si_topo = 1.02 * desn / (alc / 1000.0)
            alca = interp_alca(mun, cg, alc)
            if alca is None: alca = 1000.0
            
            si_comp = -1.0 * si_topo * 0.13 if mun == "PR" else 0.0
            si_tot = si_topo + si_comp
            elv = alca - (si_tot if mun == "PR" else si_topo)
            
            self.lbl_r2.text = f"Si Topo: {si_topo:.2f} mils\nSi Comp: {si_comp:.2f} mils\nAlça: {alca:.2f} mils\nELEVACAO FINAL: {elv:.1f} mils"
        except Exception as e:
            self.lbl_r2.text = f"Erro: {e}"

if __name__ == '__main__':
    Calc120App().run()
"""

with open("main.py", "w", encoding="utf-8") as f:
    f.write(kivy_code)

# 3. Criar buildozer.spec
print("\n⚙️ [3/5] Configurando buildozer.spec...")
spec_code = """[app]
title = Genesis M120
package.name = genesism120
package.domain = org.artilharia.morteiro
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
[buildozer]
log_level = 2
warn_on_root = 1
"""

with open("buildozer.spec", "w", encoding="utf-8") as f:
    f.write(spec_code)

# 4. Executar Compilação
print("\n🛠️ [4/5] Executando compilação do APK (pode levar de 5 a 8 minutos)...")
ret = os.system("buildozer -v android debug")

if ret == 0:
    print("\n🎉 [5/5] Compilação concluída com SUCESSO!")
    if os.path.exists("bin"):
        apk_files = [f for f in os.listdir("bin") if f.endswith(".apk")]
        if apk_files:
            apk_path = os.path.join("bin", apk_files[0])
            print(f"📦 APK gerado: {apk_path}")
            try:
                from google.colab import files
                print("⬇️ Iniciando download automático do APK...")
                files.download(apk_path)
            except ImportError:
                print(f"O arquivo APK está localizado em: {os.path.abspath(apk_path)}")
else:
    print("\n❌ Ocorreu um erro durante a compilação. Verifique os logs acima.")
