#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project: nUpmix v1.5
Description: Advanced GUI-based Audio Upmixer for Home Theater Receivers & Cinematic Archives.
             Features: Autonomous Telemetry Engine (Bitrate & Phase Correlation Analysis),
             Smart 3-Way Routing (5.1 Atmos, 3.1 Purist, 3.1 Mono), Two-Stems Vocal Isolation,
             Pure 100% Dynamic Range (Zero Limiters), 80Hz LFE Lowpass, L-R Rear Matrix,
             De-Esser Shield (Center Only), Mid-Point Smart Preview, Multi-Format Subtitle Muxing.
"""

import sys
import os
import json
import subprocess
import shutil
import tempfile
import platform
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QListWidget, 
                             QComboBox, QCheckBox, QProgressBar, QMessageBox, 
                             QListWidgetItem, QFrame, QSlider, QTabWidget, QTextEdit, 
                             QInputDialog, QSizePolicy, QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices, QPainter, QFont, QPen, QColor

# --- TEMA & STİL ---
MAC_DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
}
QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #e0e0e0;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #333333;
    border-radius: 6px;
    background-color: #252526;
    margin-top: -1px;
}
QTabBar::tab {
    background-color: #2d2d30;
    color: #9d9d9d;
    padding: 8px 16px;
    min-width: 120px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #333333;
    border-bottom: none;
}
QTabBar::tab:selected {
    background-color: #252526;
    color: #ffffff;
    font-weight: bold;
}
QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 5px;
    outline: none;
}
QListWidget::item {
    padding: 5px;
    border-bottom: 1px solid #2d2d30;
}
QListWidget::item:alternate {
    background-color: #252526;
}
QListWidget::item:selected {
    background-color: #0A84FF;
    color: white;
    border-radius: 4px;
}
QFrame {
    background-color: #252526;
    border: 1px solid #333333;
    border-radius: 8px;
}
QPushButton {
    background-color: #333333;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #404040;
    border: 1px solid #555555;
}
QPushButton:pressed {
    background-color: #0A84FF;
    border: 1px solid #0A84FF;
}
QPushButton:disabled {
    background-color: #1e1e1e;
    color: #666666;
    border: 1px solid #333333;
}
QComboBox {
    background-color: #333333;
    color: white;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px 8px;
}
QSlider::groove:horizontal {
    border: 1px solid #333333;
    height: 6px;
    background: #1e1e1e;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #0A84FF;
    border: 1px solid #0A84FF;
    width: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QProgressBar {
    border: 1px solid #333333;
    border-radius: 6px;
    text-align: center;
    background-color: #1e1e1e;
    color: white;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #30D158;
    border-radius: 5px;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #1e1e1e;
}
QCheckBox::indicator:checked {
    background-color: #0A84FF;
    border: 1px solid #0A84FF;
}
QCheckBox::indicator:disabled {
    background-color: #1e1e1e;
    border: 1px solid #333333;
}
QLabel {
    border: none;
    background: transparent;
}
QTextEdit {
    background-color: #111111;
    color: #30D158;
    font-family: "Courier New", monospace;
    font-size: 11px;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 6px;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QWidget#scrollContent {
    background-color: transparent;
}
"""

# --- ÇİFT DİL SÖZLÜĞÜ ---
LANG_DICT = {
    "TR": {
        "win_title": "nUpmix v1.0",
        "tab_main": "İşlem Merkezi",
        "tab_about": "Hakkında",
        "info_lbl": "Sadece Stereo (2.0) ve Mono (1.0) video dosyalarını sürükleyin. Çoklu kanallar reddedilir.",
        "track_lbl": "İşlenecek Ses İzi (Track):",
        "lbl_format": "Hedef Format & Çıkış:",
        "lbl_dsp": "Dinamik DSP Kontrolleri:",
        "lbl_filters": "Akustik Filtreler:",
        "lbl_ai": "Muxing & Sistem:",
        "chk_rename": "Akıllı Dosya İsimlendirme (DSP etiketlerini ekler)",
        "chk_norm": "Emniyet Zırhı (True Peak Limiter)",
        "chk_highpass": "Dip Gürültü Kesici (50Hz)",
        "chk_dynaudnorm": "Dinamik Ses Dengeleyici",
        "chk_sub": "Otonom Altyazı Göm (TR->Forced)",
        "chk_nvenc": "NVENC Hızlı Önizleme Hızlandırıcı",
        "preset_lbl": "Ayar Profilleri:",
        "btn_save_preset": "💾 Ayarı Kaydet",
        "btn_load_preset": "📂 Profili Yükle",
        "log_wait": "Sistem Beklemede...",
        "btn_clear": "Kuyruğu Temizle",
        "btn_open_dir": "📂 Çıktı Klasörünü Aç",
        "btn_preview": "👁️ 15 Sn. Orta-Sahne Önizleme",
        "btn_cancel": "⛔ İPTAL ET",
        "btn_start": "🚀 İşlemeye Başla",
        "msg_queue_empty": "Kuyruk boş!",
        "dlg_save_title": "Profili Kaydet",
        "dlg_save_msg": "Profil Adı:",
        "telemetry_lbl": "[TELEMETRİ VE OTONOM MOTOR KARAR EKRANI]",
        "tt_rename": "Çıktı dosyasına LFE, C ve H kazanç değerlerini künye olarak yazar.",
        "tt_lfe": "Subwoofer (LFE) Kanalı Güçlendirici\nÖnerilen Değer: 3 - 5 dB",
        "tt_center": "Diyalog Vurgusu (Merkez Kanal Ayarı)\nÖnerilen Değer: 4 - 6 dB",
        "tt_haas": "Haas Efekti Surround Gecikmesi\nÖnerilen Değer: 10 - 20 ms",
        "tt_bitrate": "Endüstri Standartları: AAC ve AC3 5.1 için maks 640.",
        "tt_norm": "Emniyet Zırhı (True Peak Limiter)\n0 dB'i aşan ses patlamalarından amfiyi korur.",
        "tt_highpass": "Dip Gürültü Kesici (50Hz)\nRüzgar uğultusu ve altyapı gürültülerini temizler.",
        "tt_dynaudnorm": "Dinamik Ses Dengeleyici\nEski filmlerdeki kısık sesleri dinamik olarak yükseltir.",
        "about_html": """
        <h2 style='color: #0A84FF; font-size: 26px; margin-bottom: 0px;'>nUpmix v1.0</h2>
        <p style='font-size: 14px; color: #a0a0a0; margin-top: 5px;'>Geliştiren: nutuzar</p>
        <hr style='border: 1px solid #333; margin-top: 15px; margin-bottom: 15px;'>
        <div style='font-size: 13px; color: #d0d0d0; line-height: 1.6;'>
        <p>nUpmix, standart stereo (2.0) ve mono (1.0) ses sinyallerini sinematik 5.1 surround düzlemine taşımak için geliştirilmiş açık kaynaklı bir ses işleme motorudur.</p>
        <p><b>Matematiksel Yaklaşım:</b><br>
        Sesi yapay efektlerle (reverb/eko) şişirmek yerine, doğrudan sinyalin doğasına odaklanır. Sol ve sağ kanallar arasındaki diferansiyel farkları (L-R) matematiksel olarak analiz ederek ortam seslerini arka kanallara ayırır (Atmosferik 5.1). Akustik faz korelasyonunun tam olduğu, yani merkezdeki sesin baskın olduğu durumlarda ise sesi bozmamak için otonom olarak "3.1 Purist" kararı alır ve arka kanalları sessizlikte bırakarak sahne netliğini korur.</p>
        <p><b>Temel Yetenekler:</b><br>
        • LFE (Subwoofer) kanalı için özel 120Hz Lowpass izolasyonu.<br>
        • Dinamik Haas gecikmeleri ile sahne genişletme imkanı.<br>
        • Sinyal tepe noktası (True Peak) koruması ve empedans sönümleyici (Alimiter).<br>
        • Modern FFmpeg altyapısı ve kayıpsız ses/video eşzamanlama.</p>
        <p style='color: #888; font-size: 12px; margin-top: 20px; font-style: italic;'>
        "Sesi değiştirmek değil, içindeki gizli alanı ortaya çıkarmak."
        </p>
        </div>
        """
    },
    "EN": {
        "win_title": "nUpmix v1.0",
        "tab_main": "Processing Center",
        "tab_about": "About",
        "info_lbl": "Drag Stereo (2.0) and Mono (1.0) video files here. Multi-channel audio is rejected.",
        "track_lbl": "Target Audio Track:",
        "lbl_format": "Target Format & Output:",
        "lbl_dsp": "Dynamic DSP Controls:",
        "lbl_filters": "Acoustic Filters:",
        "lbl_ai": "Muxing & System:",
        "chk_rename": "Smart Renaming (Appends tags)",
        "chk_norm": "Safety Armor (True Peak Limiter)",
        "chk_highpass": "Highpass Filter (50Hz)",
        "chk_dynaudnorm": "Dynamic Audio Normalizer",
        "chk_sub": "Auto Mux Subtitles",
        "chk_nvenc": "NVENC Fast Preview Accelerator",
        "preset_lbl": "Settings Presets:",
        "btn_save_preset": "💾 Save Preset",
        "btn_load_preset": "📂 Load Preset",
        "log_wait": "System Idle...",
        "btn_clear": "Clear Queue",
        "btn_open_dir": "📂 Open Output Folder",
        "btn_preview": "👁️ 15 Sec. Mid-Scene Preview",
        "btn_cancel": "⛔ CANCEL",
        "btn_start": "🚀 Start Processing",
        "msg_queue_empty": "Queue is empty!",
        "dlg_save_title": "Save Preset",
        "dlg_save_msg": "Preset Name:",
        "telemetry_lbl": "[TELEMETRY & AUTONOMOUS ENGINE LOGS]",
        "tt_rename": "Writes LFE, Center, and Haas gains into the output filename.",
        "tt_lfe": "Subwoofer (LFE) Channel Booster\nRecommended: 3 - 5 dB",
        "tt_center": "Dialog Boost (Center Channel)\nRecommended: 4 - 6 dB",
        "tt_haas": "Haas Effect Surround Delay\nRecommended: 10 - 20 ms",
        "tt_bitrate": "Standards: AAC max 640, AC3 5.1=max 640.",
        "tt_norm": "Safety Armor (True Peak Limiter)\nPrevents amplifier clipping above 0 dBFS.",
        "tt_highpass": "Highpass Filter (50Hz)\nRemoves low-end rumble and infrastructure noise.",
        "tt_dynaudnorm": "Dynamic Audio Normalizer\nSmooths out quiet dialogues dynamically.",
        "about_html": """
        <h2 style='color: #0A84FF; font-size: 26px; margin-bottom: 0px;'>nUpmix v1.0</h2>
        <p style='font-size: 14px; color: #a0a0a0; margin-top: 5px;'>Developer: nutuzar</p>
        <hr style='border: 1px solid #333; margin-top: 15px; margin-bottom: 15px;'>
        <div style='font-size: 13px; color: #d0d0d0; line-height: 1.6;'>
        <p>nUpmix is an open-source audio processing engine designed to transition standard stereo (2.0) and mono (1.0) signals into a cinematic 5.1 surround space.</p>
        <p><b>Mathematical Approach:</b><br>
        Rather than artificially inflating the audio with reverb or echo, it focuses directly on the nature of the signal. It mathematically analyzes the differential differences (L-R) between the left and right channels to extract ambient sounds to the rear channels (Atmospheric 5.1). When acoustic phase correlation is perfect—meaning the center sound is dominant—it autonomously decides on a "3.1 Purist" approach, leaving the rear channels in silence to preserve scene clarity.</p>
        <p><b>Core Capabilities:</b><br>
        • Dedicated 120Hz Lowpass isolation for the LFE (Subwoofer) channel.<br>
        • Soundstage expansion using dynamic Haas delays.<br>
        • True Peak protection and impedance dampening (Alimiter).<br>
        • Modern FFmpeg infrastructure with lossless A/V synchronization.</p>
        <p style='color: #888; font-size: 12px; margin-top: 20px; font-style: italic;'>
        "Not to alter the sound, but to reveal the hidden space within it."
        </p>
        </div>
        """
    }
}

def is_nvenc_available():
    try:
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            res = subprocess.run(["ffmpeg", "-h", "encoder=h264_nvenc"], capture_output=True, text=True, startupinfo=startupinfo)
        else:
            res = subprocess.run(["ffmpeg", "-h", "encoder=h264_nvenc"], capture_output=True, text=True)
        if "h264_nvenc" in res.stdout or "h264_nvenc" in res.stderr:
            return True
        return False
    except:
        return False

class FFmpegWorker(QThread):
    progress_update = pyqtSignal(int, int)
    file_status_update = pyqtSignal(str)
    console_log_update = pyqtSignal(str)
    telemetry_update = pyqtSignal(str)
    preview_ready = pyqtSignal(str)
    all_finished = pyqtSignal()

    def __init__(self, queue_files, settings_dict):
        super().__init__()
        self.queue_files = queue_files
        self.settings = settings_dict
        self.is_running = True
        self.active_processes = []

    def run_cmd(self, cmd, capture=True):
        kwargs = {}
        if platform.system() == "Windows":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'] = si
        if capture:
            return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs)
        else:
            return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, **kwargs)

    def get_audio_metadata(self, file_path, track_idx):
        meta = {"channels": 2, "bitrate": 0, "codec": "unk", "duration": 0.0}
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-show_format", str(file_path)]
        try:
            res = self.run_cmd(cmd)
            data = json.loads(res.stdout)
            
            if "format" in data and "duration" in data["format"]:
                meta["duration"] = float(data["format"]["duration"])
                
            audio_streams = [s for s in data.get("streams", []) if s.get("codec_type") == "audio"]
            if track_idx < len(audio_streams):
                stream = audio_streams[track_idx]
                meta["channels"] = int(stream.get("channels", 2))
                meta["codec"] = stream.get("codec_name", "unk")
                br = stream.get("bit_rate")
                if not br and "format" in data:
                    br = data["format"].get("bit_rate")
                if br:
                    meta["bitrate"] = int(br)
        except Exception:
            pass
        return meta

    def analyze_phase_correlation(self, file_path, track_idx, mid_time):
        cmd = [
            "ffmpeg", "-y", "-ss", str(mid_time), "-t", "5", 
            "-i", str(file_path), "-map", f"0:a:{track_idx}", 
            "-af", "aphasemeter=video=0", "-f", "null", "-"
        ]
        try:
            res = self.run_cmd(cmd)
            lines = res.stderr.splitlines()
            phase_mean = 0.0
            for line in reversed(lines):
                if "phase_mean:" in line:
                    match = re.search(r"phase_mean:\s*([\-\d\.]+)", line)
                    if match:
                        phase_mean = float(match.group(1))
                        return phase_mean
            return 0.0
        except:
            return 0.0

    def has_subtitles(self, file_path):
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-select_streams", "s", str(file_path)]
        try:
            res = self.run_cmd(cmd)
            data = json.loads(res.stdout)
            if "streams" in data and len(data["streams"]) > 0:
                return True
            return False
        except:
            return False

    # run_demucs removed

    def process_single_file(self, file_path):
        if not self.is_running:
            return False, "İşlem iptal edildi."

        path_obj = Path(file_path)
        output_dir = path_obj.parent / "nUpmix_Outputs"
        output_dir.mkdir(exist_ok=True)
        
        format_idx = self.settings["format_idx"] 
        lfe_gain = self.settings["slider_lfe"]
        center_gain = self.settings["slider_center"]
        haas_ms = self.settings["slider_haas"]
        smart_rename = self.settings["smart_rename"]
        auto_sub = self.settings["auto_sub"]
        is_preview = self.settings.get("is_preview", False)
        
        # --- ERANGE KALKANI (MAX BITRATE CLAMPING) ---
        custom_bitrate = self.settings["slider_bitrate"]
        if format_idx == 0 and custom_bitrate > 640:
            custom_bitrate = 640
        elif format_idx == 1 and custom_bitrate > 1024:
            custom_bitrate = 1024
            
        use_nvenc = self.settings.get("use_nvenc", False)
        track_idx = self.settings["track_idx"]
        temp_dir = None

        # --- TELEMETRİ VE OTONOM TEŞHİS ---
        meta = self.get_audio_metadata(file_path, track_idx)
        channels = meta["channels"]
        
        # KURAL 1: Çoklu kanal reddi. Sadece 1.0 Mono veya 2.0 Stereo işlenir.
        if channels > 2:
            err_msg = f"HATA: {channels} Kanal tespit edildi. nUpmix v1.7 sadece 2.0 Stereo ve 1.0 Mono kabul eder. ({path_obj.name})"
            self.telemetry_update.emit(f"[REDDEDİLDİ] {err_msg}")
            return False, err_msg

        bitrate_kbps = meta["bitrate"] // 1000 if meta["bitrate"] else 0
        mid_duration = max(0, meta["duration"] / 2.0) 
        
        op_mode = "3.1 Purist"
        phase_corr = 0.0

        # KURAL 2: 3-Yollu Otonom Motor Karar Mekanizması
        if channels == 1:
            op_mode = "Modernize 3.1 Mono"
            phase_corr = 1.0
        else:
            phase_corr = self.analyze_phase_correlation(file_path, track_idx, max(0, mid_duration - 5.0))
            if phase_corr > 0.95:
                op_mode = "3.1 Purist"
            elif bitrate_kbps > 0 and bitrate_kbps <= 128:
                op_mode = "3.1 Purist"
            else:
                op_mode = "5.1 Atmosferik"

        if format_idx != 0:
            op_mode = "Bypass / Basic"

        telemetry_log = (
            f"--- TELEMETRİ RAPORU: {path_obj.name} ---\n"
            f"Codec: {meta['codec'].upper()} | Bitrate: {bitrate_kbps} kbps\n"
            f"Kanal Geometrisi: {channels} CH\n"
            f"Faz Korelasyonu (Mid-Scene): {phase_corr:.2f}\n"
            f"OTONOM KARAR: [ MOD: {op_mode} ]\n"
            f"----------------------------------------"
        )
        self.telemetry_update.emit(telemetry_log)

        # --- İSİMLENDİRME ---
        dsp_tags = ""
        if smart_rename:
            tag_lfe = f"_LFE{lfe_gain}" if lfe_gain > 0 else ""
            tag_center = f"_C{center_gain}" if center_gain > 0 else ""
            tag_haas = f"_H{haas_ms}" if haas_ms > 0 else ""
            dsp_tags = f"{tag_lfe}{tag_center}{tag_haas}"

        abitrate = f"{custom_bitrate}k"
        
        out_codec_tag = "AC3_5.1" if format_idx == 0 else "AAC_2.0"
        acodec = "ac3" if format_idx == 0 else "aac"
        out_file = output_dir / f"{path_obj.stem}_[{out_codec_tag}_{abitrate}{dsp_tags}].mkv"

        if is_preview:
            out_file = output_dir / f"PREVIEW_{path_obj.stem}.mkv"

        inputs = [str(path_obj)]
        vid_in = 0

        try:

            # --- MUXING SUBS ---
            has_embedded_subs = self.has_subtitles(str(path_obj))
            external_subs = []
            
            if auto_sub and not has_embedded_subs:
                valid_sub_exts = [".srt", ".ass", ".ssa", ".vtt", ".sub"]
                possible_subs = []
                for ext in valid_sub_exts:
                    possible_subs.extend(list(path_obj.parent.glob(f"{path_obj.stem}*{ext}")))
                
                for sub in possible_subs:
                    sub_lower = sub.stem.lower()
                    is_tr = any(x in sub_lower for x in ["-tr", "_tr", ".tr", "-tur", "_tur", ".tur", " tr", " tur"])
                    is_en = any(x in sub_lower for x in ["-en", "_en", ".en", "-eng", "_eng", ".eng", " en", " eng"])
                    
                    if is_tr:
                        external_subs.append({"path": sub, "type": "TR"})
                    elif is_en:
                        external_subs.append({"path": sub, "type": "EN"})

            # --- ACOUSTIC FILTERS ---
            pre_pan_filters = []
            post_pan_filters = []
            
            if self.settings["use_norm"]: 
                # Emniyet Zırhı (True Peak Limiter)
                post_pan_filters.append("alimiter=limit=-0.5dB:attack=5:release=50")
            if self.settings["use_highpass"]: 
                post_pan_filters.append("highpass=f=50")
            if self.settings.get("use_dynaudnorm"):
                post_pan_filters.append("dynaudnorm=p=0.9:m=10:s=5")
            
            # Senkron zırhı ve son örnekleme tek satırda birleştirildi
            post_pan_filters.append("aresample=48000:async=1000")

            cmd = ["ffmpeg", "-y", "-fflags", "+genpts"]
            
            if is_preview:
                cmd.extend(["-ss", str(mid_duration), "-t", "15"])
            cmd.extend(["-i", inputs[0]])

            for inp in inputs[1:]:
                cmd.extend(["-i", inp])
                
            sub_start_idx = len(inputs)
            for sub_dict in external_subs:
                if is_preview:
                    cmd.extend(["-ss", str(mid_duration), "-t", "15"])
                cmd.extend(["-i", str(sub_dict["path"])])

            cmd.extend(["-map", f"{vid_in}:v"])
            
            # --- MATRIX ENGINE (PURE MATH) ---
            if format_idx == 0:
                fc_val = round(0.35 * (1.0 + (center_gain / 10.0)), 3)
                lfe_val = round(0.5 * (1.0 + (lfe_gain / 10.0)), 3)
                fc_mono = round(1.0 + (center_gain / 10.0), 3)
                
                if op_mode == "Modernize 3.1 Mono":
                    # Mono: Ön sahneler kopyalanır, arka kanallar SIFIR.
                    complex_filter = (
                        f"[0:a:{track_idx}]pan=stereo|c0=c0|c1=c0[orig_stereo];"
                        f"[orig_stereo]asplit=2[orig_front][orig_lfe_raw];"
                        f"[orig_lfe_raw]lowpass=f=120[lfe_filtered];"
                        f"[orig_front][lfe_filtered]amerge=inputs=2[aout];"
                        f"[aout]pan=5.1|"
                        f"FC={fc_mono}*c0|"
                        f"FL=c0|"
                        f"FR=c1|"
                        f"LFE={lfe_val}*c2 + {lfe_val}*c3|"
                        f"BL=0*c0|"
                        f"BR=0*c0[panout]"
                    )
                elif op_mode == "3.1 Purist":
                    # Stereo Purist: Ön kanallar orijinal, arka kanallar SIFIR.
                    complex_filter = (
                        f"[0:a:{track_idx}]asplit=2[orig_front][orig_lfe_raw];"
                        f"[orig_lfe_raw]lowpass=f=120[lfe_filtered];"
                        f"[orig_front][lfe_filtered]amerge=inputs=2[aout];"
                        f"[aout]pan=5.1|"
                        f"FC={fc_val}*c0 + {fc_val}*c1|"
                        f"FL=c0|"
                        f"FR=c1|"
                        f"LFE={lfe_val}*c2 + {lfe_val}*c3|"
                        f"BL=0*c0|"
                        f"BR=0*c0[panout]"
                    )
                else: # 5.1 Atmosferik
                    # Stereo -> L-R Diferansiyel Fark Matrisi
                    complex_filter = (
                        f"[0:a:{track_idx}]asplit=3[orig_front][orig_lfe_raw][orig_rear_raw];"
                        f"[orig_lfe_raw]lowpass=f=120[lfe_filtered];"
                        f"[orig_rear_raw]highpass=f=300[rear_filtered];"
                        f"[orig_front][lfe_filtered][rear_filtered]amerge=inputs=3[aout];"
                        f"[aout]pan=5.1|"
                        f"FC={fc_val}*c0 + {fc_val}*c1|"
                        f"FL=c0|"
                        f"FR=c1|"
                        f"LFE={lfe_val}*c2 + {lfe_val}*c3|"
                        f"BL=0.5*c4 + -0.5*c5|"
                        f"BR=0.5*c5 + -0.5*c4[panout_pre]"
                    )
                    if haas_ms > 0:
                        complex_filter += f";[panout_pre]adelay=0|0|0|0|{haas_ms}|{haas_ms}[panout]"
                    else:
                        complex_filter += f";[panout_pre]anull[panout]"

                dsp_chain = []
                if pre_pan_filters: dsp_chain.extend(pre_pan_filters)
                if post_pan_filters: dsp_chain.extend(post_pan_filters)
                
                if dsp_chain:
                    complex_filter += f";[panout]{','.join(dsp_chain)}[finala]"
                else:
                    complex_filter += ";[panout]anull[finala]"
                    
                cmd.extend(["-filter_complex", complex_filter, "-map", "[finala]"])

            else: 
                cmd.extend(["-map", f"{vid_in}:a:{track_idx}"])
                full_filter_chain = []
                
                if center_gain > 0:
                    full_filter_chain.append(f"equalizer=f=1500:width_type=h:width=200:g={center_gain}")
                
                if post_pan_filters:
                    full_filter_chain.extend(post_pan_filters)

                if full_filter_chain:
                    final_filter = ",".join(full_filter_chain)
                    cmd.extend(["-af", final_filter])

            # --- MUXING SUBS ---
            if has_embedded_subs:
                cmd.extend(["-map", f"{vid_in}:s?"])
                cmd.extend(["-c:s", "copy"])
            elif external_subs:
                dispositions = []
                sub_counter = 0
                for i, sub_dict in enumerate(external_subs):
                    current_input_idx = sub_start_idx + i
                    cmd.extend(["-map", f"{current_input_idx}:s"])
                    if sub_dict["type"] == "TR":
                        dispositions.extend([
                            f"-disposition:s:{sub_counter}", "default+forced",
                            f"-metadata:s:s:{sub_counter}", "language=tur",
                            f"-metadata:s:s:{sub_counter}", "title=Turkish"
                        ])
                    else:
                        dispositions.extend([
                            f"-disposition:s:{sub_counter}", "none",
                            f"-metadata:s:s:{sub_counter}", "language=eng",
                            f"-metadata:s:s:{sub_counter}", "title=English"
                        ])
                    sub_counter += 1
                cmd.extend(["-c:s", "copy"])
                cmd.extend(dispositions)
            else:
                cmd.extend(["-map", f"{vid_in}:s?"])
                cmd.extend(["-c:s", "copy"])

            if is_preview:
                if use_nvenc:
                    cmd.extend(["-c:v", "h264_nvenc", "-preset", "fast", "-cq", "28"])
                else:
                    cmd.extend(["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28"])
            else:
                cmd.extend(["-c:v", "copy"])

            cmd.extend(["-c:a", acodec, "-b:a", abitrate, "-ar", "48000", "-map_metadata", "0", "-avoid_negative_ts", "make_zero"])
            cmd.append(str(out_file))

            self.file_status_update.emit(f"İşleniyor: {path_obj.name}")
            
            kwargs = {}
            if platform.system() == "Windows":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                kwargs['startupinfo'] = si
                
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, **kwargs)
            self.active_processes.append(process)
            
            last_err_line = ""
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    last_err_line = line.strip()
            
            if process in self.active_processes:
                self.active_processes.remove(process)

            if not self.is_running:
                if out_file.exists():
                    try: out_file.unlink()
                    except: pass
                return False, f"[!] İptal Edildi: {path_obj.name}"

            if process.returncode == 0:
                if is_preview:
                    self.preview_ready.emit(str(out_file))
                    return True, f"[~] Önizleme Hazır: {out_file.name}"
                return True, f"[+] Başarılı: {path_obj.name}"
            else:
                if not is_preview:
                    self.console_log_update.emit(f"[!] Zaman Damgası/Kopya Hatası ({path_obj.name}). Oto-Onarım (Re-encode) devrede...")
                    try:
                        idx = cmd.index("-c:v")
                        if cmd[idx+1] == "copy":
                            cmd.pop(idx+1)
                            cmd.pop(idx)
                            if use_nvenc:
                                cmd.extend(["-c:v", "h264_nvenc", "-preset", "fast", "-cq", "28"])
                            else:
                                cmd.extend(["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28"])
                            
                            self.file_status_update.emit(f"Onarılıyor: {path_obj.name}")
                            
                            kwargs = {}
                            if platform.system() == "Windows":
                                si = subprocess.STARTUPINFO()
                                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                                kwargs['startupinfo'] = si
                                
                            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, **kwargs)
                            self.active_processes.append(process)
                            
                            while True:
                                line = process.stderr.readline()
                                if not line and process.poll() is not None:
                                    break
                                if line:
                                    last_err_line = line.strip()
                                    
                            if process in self.active_processes:
                                self.active_processes.remove(process)
                                
                            if process.returncode == 0:
                                return True, f"[+] Başarılı (Oto-Onarım): {path_obj.name}"
                    except Exception as e:
                        pass
                
                try:
                    with open("nUpmix_error.log", "a", encoding="utf-8") as lf:
                        lf.write(f"\n--- HATA: {path_obj.name} ---\nFFmpeg Kodu: {process.returncode}\nSon Satır: {last_err_line}\n")
                except: pass
                
                self.console_log_update.emit(f"FFmpeg Hatası ({process.returncode}): Hata detayı için nUpmix_error.log dosyasına bakınız.")
                return False, f"[-] FFmpeg Hatası ({path_obj.name})"
                
        except Exception as e:
            self.console_log_update.emit(f"Sistem Kritik Hatası: {str(e)}")
            return False, f"[-] Sistem Hatası ({path_obj.name})"
        finally:
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass

    def run(self):
        total_files = len(self.queue_files)
        completed = 0
        
        if self.settings.get("is_preview", False):
            max_workers = 1
        else:
            max_workers = min(os.cpu_count() or 4, total_files)
            
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.process_single_file, f): f for f in self.queue_files}
            
            for future in as_completed(futures):
                try:
                    success, result_str = future.result()
                except Exception as e:
                    success, result_str = False, f"Bilinmeyen Hata: {str(e)}"
                    
                if self.is_running:
                    completed += 1
                    self.file_status_update.emit(f"[{completed}/{total_files}] {result_str}")
                    self.progress_update.emit(completed, total_files)

        self.all_finished.emit()

    def stop(self):
        self.is_running = False
        for process in self.active_processes:
            try:
                if platform.system() == "Windows":
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    process.terminate()
                    process.kill()
            except Exception:
                pass
        self.active_processes.clear()


class DropListWidget(QListWidget):
    file_dropped = pyqtSignal(list)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0:
            painter = QPainter(self.viewport())
            painter.setPen(QPen(QColor("#666666")))
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            lang = getattr(self.window(), 'current_lang', 'TR')
            text = "📥 Lütfen İşlenecek Video Dosyalarını Buraya Sürükleyip Bırakın 📥" if lang == "TR" else "📥 Please Drag and Drop Video Files Here 📥"
            painter.drawText(self.viewport().rect(), Qt.AlignCenter, text)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlternatingRowColors(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = [str(u.toLocalFile()) for u in event.mimeData().urls() if u.isLocalFile()]
            self.file_dropped.emit(links)
        else: event.ignore()


class nUpmixApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_lang = "TR"
        self.setGeometry(100, 100, 900, 750)
        
        self.queue = []
        self.worker = None
        self.last_output_dir = None
        self.presets_file = Path(os.path.expanduser("~")) / ".nupmix_presets_v16.json"
        
        self.init_ui()
        self.load_presets_to_combo()
        self.update_ui_texts()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["TR", "EN"])
        self.lang_combo.currentTextChanged.connect(self.change_language)
        self.lang_combo.setMinimumWidth(60)
        self.tabs.setCornerWidget(self.lang_combo, Qt.TopRightCorner)

        self.main_tab = QWidget()
        self.main_tab_layout = QVBoxLayout(self.main_tab)
        
        self.scroll_layout = self.main_tab_layout

        self.build_main_tab_content()

        self.tabs.addTab(self.main_tab, "İşlem Merkezi")

        self.about_tab = QWidget()
        self.init_about_tab()
        self.tabs.addTab(self.about_tab, "Hakkında")

    def build_main_tab_content(self):
        top_controls_layout = QHBoxLayout()
        
        self.info_lbl = QLabel()
        self.info_lbl.setStyleSheet("color: #9d9d9d; margin-bottom: 5px; font-size: 14px;")
        top_controls_layout.addWidget(self.info_lbl)
        top_controls_layout.addStretch()

        self.track_lbl = QLabel()
        top_controls_layout.addWidget(self.track_lbl)
        self.track_combo = QComboBox()
        self.track_combo.addItems(["0", "1", "2", "3"])
        self.track_combo.setMinimumWidth(80)
        top_controls_layout.addWidget(self.track_combo)
        self.scroll_layout.addLayout(top_controls_layout)

        drop_layout = QHBoxLayout()
        drop_layout.setContentsMargins(10, 5, 10, 5)

        self.main_title_lbl = QLabel("nUpmix\nv1.0")
        self.main_title_lbl.setStyleSheet("font-family: 'Segoe UI Black', Arial; font-size: 26px; font-weight: bold; color: #0A84FF; padding-right: 15px;")
        self.main_title_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        drop_layout.addWidget(self.main_title_lbl, 1)

        self.list_widget = DropListWidget(self)
        self.list_widget.setMinimumHeight(60)
        self.list_widget.file_dropped.connect(self.add_to_queue)
        drop_layout.addWidget(self.list_widget, 6)

        right_spacer = QLabel()
        drop_layout.addWidget(right_spacer, 1)

        self.scroll_layout.addLayout(drop_layout)

        panels_layout = QHBoxLayout()

        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setSpacing(6)
        
        self.lbl_format = QLabel()
        self.lbl_format.setStyleSheet("font-weight: bold; color: #0A84FF; font-size: 14px;")
        left_layout.addWidget(self.lbl_format)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["AC3 5.1 Surround", "AAC 2.0 Stereo"])
        self.format_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.format_combo.setCurrentIndex(0)
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        left_layout.addWidget(self.format_combo)
        
        self.chk_rename = QCheckBox()
        self.chk_rename.setChecked(True)
        left_layout.addWidget(self.chk_rename)

        left_layout.addSpacing(5)
        
        self.lbl_dsp = QLabel()
        self.lbl_dsp.setStyleSheet("font-weight: bold; color: #0A84FF; font-size: 14px;")
        left_layout.addWidget(self.lbl_dsp)

        self.lbl_bitrate = QLabel("Çıktı Bit Hızı (Bitrate): 640 kbps")
        left_layout.addWidget(self.lbl_bitrate)
        self.slider_bitrate = QSlider(Qt.Horizontal)
        self.slider_bitrate.setRange(320, 640)
        self.slider_bitrate.setSingleStep(128)
        self.slider_bitrate.setTickInterval(128)
        self.slider_bitrate.setTickPosition(QSlider.TicksBelow)
        self.slider_bitrate.setValue(640)
        self.slider_bitrate.valueChanged.connect(self.on_bitrate_changed)
        left_layout.addWidget(self.slider_bitrate)

        self.lbl_lfe = QLabel("LFE: 0 dB")
        left_layout.addWidget(self.lbl_lfe)
        self.slider_lfe = QSlider(Qt.Horizontal)
        self.slider_lfe.setRange(0, 10)
        self.slider_lfe.setValue(0)
        self.slider_lfe.valueChanged.connect(lambda v: self.lbl_lfe.setText(f"LFE: {v} dB"))
        left_layout.addWidget(self.slider_lfe)

        self.lbl_center = QLabel("Center: 0 dB")
        left_layout.addWidget(self.lbl_center)
        self.slider_center = QSlider(Qt.Horizontal)
        self.slider_center.setRange(0, 10)
        self.slider_center.setValue(0)
        self.slider_center.valueChanged.connect(lambda v: self.lbl_center.setText(f"Center: {v} dB"))
        left_layout.addWidget(self.slider_center)

        self.lbl_haas = QLabel("Haas: 0 ms")
        left_layout.addWidget(self.lbl_haas)
        self.slider_haas = QSlider(Qt.Horizontal)
        self.slider_haas.setRange(0, 30)
        self.slider_haas.setValue(0)
        self.slider_haas.valueChanged.connect(lambda v: self.lbl_haas.setText(f"Haas: {v} ms"))
        left_layout.addWidget(self.slider_haas)

        panels_layout.addWidget(left_frame, 4)

        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)

        self.lbl_filters = QLabel()
        self.lbl_filters.setStyleSheet("font-weight: bold; color: #30D158; font-size: 14px;")
        right_layout.addWidget(self.lbl_filters)

        self.chk_norm = QCheckBox()
        self.chk_norm.setChecked(True)
        self.chk_highpass = QCheckBox()
        self.chk_highpass.setChecked(False)
        self.chk_dynaudnorm = QCheckBox()
        self.chk_dynaudnorm.setChecked(False)

        filter_grid = QGridLayout()
        filter_grid.addWidget(self.chk_norm, 0, 0)
        filter_grid.addWidget(self.chk_highpass, 0, 1)
        filter_grid.addWidget(self.chk_dynaudnorm, 1, 0, 1, 2)
        right_layout.addLayout(filter_grid)
        
        right_layout.addSpacing(10)

        self.lbl_ai = QLabel()
        self.lbl_ai.setStyleSheet("font-weight: bold; color: #FF9F0A; font-size: 14px;")
        right_layout.addWidget(self.lbl_ai)

        self.chk_sub = QCheckBox()
        self.chk_sub.setChecked(True)
        
        ai_grid = QGridLayout()
        
        self.chk_nvenc = QCheckBox()
        nvenc_ok = is_nvenc_available()
        if nvenc_ok:
            self.chk_nvenc.setChecked(True)
        else:
            self.chk_nvenc.setEnabled(False)

        ai_grid.addWidget(self.chk_sub, 0, 0)
        ai_grid.addWidget(self.chk_nvenc, 0, 1)
        right_layout.addLayout(ai_grid)
        
        right_layout.addSpacing(10)
        self.preset_lbl = QLabel()
        self.preset_lbl.setStyleSheet("font-weight: bold; color: #0A84FF; font-size: 14px;")
        right_layout.addWidget(self.preset_lbl)

        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(150)
        right_layout.addWidget(self.preset_combo)
        
        preset_btns = QHBoxLayout()
        self.btn_save_preset = QPushButton()
        self.btn_save_preset.clicked.connect(self.save_preset)
        preset_btns.addWidget(self.btn_save_preset)
        
        self.btn_load_preset = QPushButton()
        self.btn_load_preset.clicked.connect(self.load_preset)
        preset_btns.addWidget(self.btn_load_preset)
        right_layout.addLayout(preset_btns)
        
        right_layout.addStretch()
        panels_layout.addWidget(right_frame, 3)

        # TELEMETRY PANEL MOVED TO PANELS LAYOUT (FAR RIGHT)
        telemetry_frame = QFrame()
        telemetry_layout = QVBoxLayout(telemetry_frame)
        
        self.telemetry_lbl = QLabel()
        self.telemetry_lbl.setStyleSheet("font-weight: bold; color: #FF453A; font-size: 13px; margin-top: 5px;")
        telemetry_layout.addWidget(self.telemetry_lbl)
        
        self.telemetry_box = QTextEdit()
        self.telemetry_box.setReadOnly(True)
        self.telemetry_box.setMinimumHeight(90)
        self.telemetry_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.telemetry_box.setStyleSheet("background-color: #0d0d0d; color: #FF9F0A; font-family: 'Courier New', monospace; font-size: 12px;")
        telemetry_layout.addWidget(self.telemetry_box)
        
        panels_layout.addWidget(telemetry_frame, 4)

        self.scroll_layout.addLayout(panels_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.main_tab_layout.addWidget(self.progress_bar)

        self.log_lbl = QLabel()
        self.log_lbl.setStyleSheet("color: #0A84FF; font-weight: bold; font-size: 14px;")
        self.main_tab_layout.addWidget(self.log_lbl)

        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton()
        self.clear_btn.clicked.connect(self.clear_queue)
        
        self.open_dir_btn = QPushButton()
        self.open_dir_btn.setEnabled(False)
        self.open_dir_btn.clicked.connect(self.open_output_directory)

        self.preview_btn = QPushButton()
        self.preview_btn.setStyleSheet("background-color: #5E5CE6; color: white; font-weight: bold; font-size: 14px;")
        self.preview_btn.clicked.connect(self.start_preview)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setStyleSheet("background-color: #FF453A; color: white; font-weight: bold; font-size: 14px;")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_processing)

        self.start_btn = QPushButton()
        self.start_btn.setStyleSheet("background-color: #30D158; color: black; font-weight: bold; font-size: 14px;")
        self.start_btn.clicked.connect(self.start_processing)

        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.open_dir_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.start_btn)
        self.main_tab_layout.addLayout(btn_layout)

    def init_about_tab(self):
        layout = QVBoxLayout(self.about_tab)
        self.about_text = QTextEdit()
        self.about_text.setReadOnly(True)
        self.about_text.setStyleSheet("background-color: #1e1e1e; border: none;")
        layout.addWidget(self.about_text)

    def change_language(self, lang_code):
        self.current_lang = lang_code
        self.update_ui_texts()

    def update_ui_texts(self):
        d = LANG_DICT[self.current_lang]
        
        self.setWindowTitle(d["win_title"])
        self.tabs.setTabText(0, d["tab_main"])
        self.tabs.setTabText(1, d["tab_about"])
        
        self.info_lbl.setText(d["info_lbl"])
        self.track_lbl.setText(d["track_lbl"])
        self.lbl_format.setText(d["lbl_format"])
        self.lbl_dsp.setText(d["lbl_dsp"])
        self.lbl_filters.setText(d["lbl_filters"])
        self.lbl_ai.setText(d["lbl_ai"])
        self.chk_rename.setText(d["chk_rename"])
        self.chk_norm.setText(d["chk_norm"])
        self.chk_highpass.setText(d["chk_highpass"])
        self.chk_dynaudnorm.setText(d["chk_dynaudnorm"])
        self.chk_sub.setText(d["chk_sub"])
        self.chk_nvenc.setText(d["chk_nvenc"])
        self.preset_lbl.setText(d.get("preset_lbl", "Ayar Profilleri:"))
        self.btn_save_preset.setText(d["btn_save_preset"])
        self.btn_load_preset.setText(d["btn_load_preset"])
        self.telemetry_lbl.setText(d["telemetry_lbl"])
        self.log_lbl.setText(d["log_wait"])
        self.clear_btn.setText(d["btn_clear"])
        self.open_dir_btn.setText(d["btn_open_dir"])
        self.preview_btn.setText(d["btn_preview"])
        self.cancel_btn.setText(d["btn_cancel"])
        self.start_btn.setText(d["btn_start"])
        self.about_text.setHtml(d["about_html"])

        self.chk_rename.setToolTip(d["tt_rename"])
        self.slider_lfe.setToolTip(d["tt_lfe"])
        self.slider_center.setToolTip(d["tt_center"])
        self.slider_haas.setToolTip(d["tt_haas"])
        self.slider_bitrate.setToolTip(d["tt_bitrate"])
        
        self.chk_norm.setToolTip(d["tt_norm"])
        self.chk_highpass.setToolTip(d["tt_highpass"])
        self.chk_dynaudnorm.setToolTip(d["tt_dynaudnorm"])
        
        cv = self.slider_bitrate.value()
        self.lbl_bitrate.setText(f"Bitrate: {cv} kbps" if self.current_lang=="EN" else f"Çıktı Bit Hızı (Bitrate): {cv} kbps")

    def on_bitrate_changed(self, v):
        if v <= 320:
            snapped = 320
        else:
            snapped = round(v / 128) * 128
            
        if self.slider_bitrate.value() != snapped:
            self.slider_bitrate.blockSignals(True)
            self.slider_bitrate.setValue(snapped)
            self.slider_bitrate.blockSignals(False)
            
        self.lbl_bitrate.setText(f"Bitrate: {snapped} kbps" if self.current_lang=="EN" else f"Çıktı Bit Hızı (Bitrate): {snapped} kbps")

    def on_format_changed(self, index):
        if index == 0: 
            # AC3 Seçildiğinde Tavan 640 olarak kitlenir
            self.slider_bitrate.setRange(320, 640)
            self.slider_bitrate.setValue(640)
            self.slider_lfe.setEnabled(True)
            self.slider_haas.setEnabled(True)
        elif index == 1: 
            # AAC Seçildiğinde Tavan 640 olarak esner
            self.slider_bitrate.setRange(128, 640)
            self.slider_bitrate.setValue(320)
            self.slider_lfe.setEnabled(False)
            self.slider_haas.setEnabled(False)
            self.slider_haas.setValue(0)
            self.slider_lfe.setValue(0)

    def get_audio_info(self, file_path):
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-select_streams", "a", str(file_path)]
        try:
            kwargs = {}
            if platform.system() == "Windows":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                kwargs['startupinfo'] = si
                
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs)
            data = json.loads(res.stdout)
            if "streams" in data and len(data["streams"]) > 0:
                streams_info = []
                for idx, s in enumerate(data["streams"]):
                    codec = s.get("codec_name", "Unk").upper()
                    channels = s.get("channels", "?")
                    sr = s.get("sample_rate", "")
                    lang = s.get("tags", {}).get("language", "und")
                    streams_info.append(f"T{idx}:{codec}({channels}CH) {sr}Hz-{lang}")
                return " | ".join(streams_info)
            return "[No Audio]"
        except: return "[Error]"

    def add_to_queue(self, files):
        valid_exts = [".mp4", ".mkv", ".avi", ".mov"]
        for f in files:
            path_obj = Path(f)
            if path_obj.is_file() and path_obj.suffix.lower() in valid_exts:
                if f not in self.queue:
                    self.queue.append(f)
                    info = self.get_audio_info(f)
                    item = QListWidgetItem(f"[{info}] -> {path_obj.name}")
                    item.setData(Qt.UserRole, f)
                    self.list_widget.addItem(item)

    def clear_queue(self):
        self.queue.clear()
        self.list_widget.clear()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.log_lbl.setText(LANG_DICT[self.current_lang]["btn_clear"] + " OK")
        self.open_dir_btn.setEnabled(False)
        self.telemetry_box.clear()

    def load_presets_to_combo(self):
        self.preset_combo.clear()
        if self.presets_file.exists():
            try:
                with open(self.presets_file, "r", encoding="utf-8") as f:
                    presets = json.load(f)
                    self.preset_combo.addItems(list(presets.keys()))
            except: pass

    def save_preset(self):
        d = LANG_DICT[self.current_lang]
        name, ok = QInputDialog.getText(self, d.get("dlg_save_title", "Save"), d.get("dlg_save_msg", "Name:"))
        if ok and name:
            presets = {}
            if self.presets_file.exists():
                try:
                    with open(self.presets_file, "r", encoding="utf-8") as f:
                        presets = json.load(f)
                except: pass
            
            presets[name] = self.get_current_settings()
            try:
                with open(self.presets_file, "w", encoding="utf-8") as f:
                    json.dump(presets, f, indent=4)
                self.load_presets_to_combo()
                self.preset_combo.setCurrentText(name)
            except Exception:
                pass

    def load_preset(self):
        name = self.preset_combo.currentText()
        if not name or not self.presets_file.exists(): return
        try:
            with open(self.presets_file, "r", encoding="utf-8") as f:
                presets = json.load(f)
                if name in presets:
                    p = presets[name]
                    self.format_combo.setCurrentIndex(p.get("format_idx", 0))
                    
                    # Güvenlik Kalkanı: AC3 Seçiliyken preset içinde yüksek bitrate gelse de ezilir
                    val = p.get("slider_bitrate", 640)
                    if p.get("format_idx", 0) == 0 and val > 640:
                        val = 640
                    self.slider_bitrate.setValue(val)
                    
                    self.slider_lfe.setValue(p.get("slider_lfe", 0))
                    self.slider_center.setValue(p.get("slider_center", 0))
                    self.slider_haas.setValue(p.get("slider_haas", 0))
                    self.chk_rename.setChecked(p.get("smart_rename", True))
                    self.chk_norm.setChecked(p.get("use_norm", False))
                    self.chk_highpass.setChecked(p.get("use_highpass", False))
                    
                    self.chk_sub.setChecked(p.get("auto_sub", True))
                    self.chk_nvenc.setChecked(p.get("use_nvenc", False) and is_nvenc_available())
        except: pass

    def get_current_settings(self):
        return {
            "format_idx": self.format_combo.currentIndex(),
            "track_idx": self.track_combo.currentIndex(),
            "slider_bitrate": self.slider_bitrate.value(),
            "slider_lfe": self.slider_lfe.value(),
            "slider_center": self.slider_center.value(),
            "slider_haas": self.slider_haas.value(),
            "smart_rename": self.chk_rename.isChecked(),
            "use_norm": self.chk_norm.isChecked(),
            "use_highpass": self.chk_highpass.isChecked(),
            "use_dynaudnorm": self.chk_dynaudnorm.isChecked(),
            "auto_sub": self.chk_sub.isChecked(),
            "use_nvenc": self.chk_nvenc.isChecked(),
            "is_preview": False
        }

    def cancel_processing(self):
        if self.worker and self.worker.isRunning():
            self.log_lbl.setText("Cancelling...")
            self.cancel_btn.setEnabled(False)
            self.worker.stop()

    def start_preview(self):
        if not self.queue:
            QMessageBox.warning(self, "Warning", LANG_DICT[self.current_lang]["msg_queue_empty"])
            return
            
        settings = self.get_current_settings()
        settings["is_preview"] = True
        self.telemetry_box.clear()
        self.execute_worker([self.queue[0]], settings, is_preview=True)

    def start_processing(self):
        if not self.queue:
            QMessageBox.warning(self, "Warning", LANG_DICT[self.current_lang]["msg_queue_empty"])
            return
        
        settings = self.get_current_settings()
        self.telemetry_box.clear()
        self.execute_worker(self.queue.copy(), settings, is_preview=False)

    def execute_worker(self, target_queue, settings, is_preview):
        self.start_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        self.progress_bar.setRange(0, 0)
        
        self.last_output_dir = Path(target_queue[0]).parent / "nUpmix_Outputs"

        mode_text = "DRY-RUN" if is_preview else "BATCH"
        self.log_lbl.setText(f"[{mode_text}] Started...")
        
        self.worker = FFmpegWorker(target_queue, settings)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.file_status_update.connect(self.update_log)
        self.worker.telemetry_update.connect(lambda line: self.telemetry_box.append(line))
        self.worker.console_log_update.connect(lambda line: self.telemetry_box.append(line))
        self.worker.preview_ready.connect(self.open_preview_file)
        self.worker.all_finished.connect(self.processing_finished)
        self.worker.start()

    def update_progress(self, completed, total):
        pass

    def update_log(self, msg):
        self.log_lbl.setText(msg)

    def open_preview_file(self, file_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def processing_finished(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        
        if not self.worker.is_running:
            self.log_lbl.setText("Operation Cancelled.")
            self.progress_bar.setValue(0)
        else:
            self.log_lbl.setText("Operation Completed Successfully!")
            
        self.start_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.open_dir_btn.setEnabled(True)
        
        if self.worker.is_running and not self.worker.settings.get("is_preview", False):
            self.list_widget.clear()
            self.queue.clear()

    def open_output_directory(self):
        if self.last_output_dir and self.last_output_dir.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.last_output_dir)))

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(MAC_DARK_STYLESHEET)
    window = nUpmixApp()
    window.show()
    sys.exit(app.exec_())