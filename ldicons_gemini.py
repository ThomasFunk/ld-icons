#!/usr/bin/env python3
__author__ = 'Thomas Funk & Gemini'
__date__ = "2026/03/04"
__version__ = "0.3.0"

import os
import sys
import argparse
import atexit
import configparser
import time
import mmap
import tempfile
import json
import select
from PIL import Image, ImageDraw, ImageFont
from pywayland.client import Display

# Pfad zu den generierten Protokollen
sys.path.append(os.path.join(os.path.dirname(__file__), 'protocols'))

from protocols.wayland.wl_compositor import WlCompositor
from protocols.wayland.zwlr_layer_shell_v1 import ZwlrLayerShellV1
from protocols.wayland.wl_shm import WlShm
from protocols.wayland.wl_seat import WlSeat
from protocols.wayland.wl_output import WlOutput

class Monitor:
    """Verwaltet die Daten und die Surface eines einzelnen physischen Bildschirms."""
    def __init__(self, output_id, wl_output):
        self.output_id = output_id
        self.wl_output = wl_output
        self.name = f"Output-{output_id}"
        self.x, self.y = 0, 0
        self.width, self.height = 0, 0
        self.surface = None
        self.layer_surface = None
        self.buffer = None
        self.shm_data = None
        self.is_ready = False
        
        # Grid-Dimensionen für diesen Monitor
        self.grid_cols = 0
        self.grid_rows = 0

    def setup_buffer(self, shm):
        """Erstellt einen Shared Memory Buffer für das Rendering auf diesem Monitor."""
        stride = self.width * 4
        size = stride * self.height
        with tempfile.TemporaryFile() as f:
            f.truncate(size)
            self.shm_data = mmap.mmap(f.fileno(), size)
            pool = shm.create_pool(f.fileno(), size)
            # Format 0x34325258 entspricht ARGB8888
            self.buffer = pool.create_buffer(0, self.width, self.height, stride, 0x34325258)
            pool.destroy()

class LDIcons:
    def __init__(self, config_path=None):
        self.monitors = {}      # Aktive Monitore: {id: Monitor-Objekt}
        self.icon_positions = {} # { "dateiname": {"monitor": "Name", "grid_x": 0, "grid_y": 0} }
        self.configured = False
        
        # Standard-Einstellungen (werden später aus Config überschrieben)
        self.grid_size = 100
        self.icon_size = 48
        
        # Wayland Initialisierung
        self.display = Display()
        self.display.connect()
        self.registry = self.display.get_registry()
        self.registry.dispatcher['global'] = self._registry_global
        
        # Speicherort für Icon-Positionen
        self.pos_file = os.path.expanduser("~/.config/ldicons/icon_positions.json")
        self.load_positions()

    def _registry_global(self, registry, id, interface, version):
        """Bindet die benötigten Wayland-Schnittstellen."""
        if interface == 'wl_output':
            # Ein neuer Monitor wurde vom Server gemeldet
            output = registry.bind(id, WlOutput, version)
            mon = Monitor(id, output)
            self.monitors[id] = mon
            # Registriere Dispatcher für Monitor-Details
            output.dispatcher['geometry'] = lambda *a: self._on_geometry(mon, *a)
            output.dispatcher['mode'] = lambda *a: self._on_mode(mon, *a)
            output.dispatcher['done'] = lambda *a: self._on_done(mon, *a)
            
        elif interface == 'wl_compositor':
            self.compositor = registry.bind(id, WlCompositor, version)
        elif interface == 'zwlr_layer_shell_v1':
            self.layer_shell = registry.bind(id, ZwlrLayerShellV1, version)
        elif interface == 'wl_shm':
            self.shm = registry.bind(id, WlShm, version)
        elif interface == 'wl_seat':
            self.seat = registry.bind(id, WlSeat, version)

    def _on_geometry(self, mon, output, x, y, pw, ph, sub, make, model, trans):
        """Wird aufgerufen, wenn der Server Monitor-Position und Name sendet."""
        mon.x, mon.y = x, y
        # Wir erzeugen einen eindeutigen Namen aus Hersteller und Modell
        mon.name = f"{make}_{model}".replace(" ", "_").replace(",", "")

    def _on_mode(self, mon, output, flags, width, height, refresh):
        """Wird aufgerufen, wenn der Server die Auflösung sendet."""
        mon.width, mon.height = width, height

    def _on_done(self, mon):
        """Wird aufgerufen, wenn alle Informationen für einen Monitor übertragen wurden."""
        mon.is_ready = True
        mon.grid_cols = mon.width // self.grid_size
        mon.grid_rows = mon.height // self.grid_size
        print(f"🖥  Monitor bereit: {mon.name} ({mon.width}x{mon.height}) an Pos {mon.x},{mon.y}")
        self.setup_monitor_surface(mon)

    def setup_monitor_surface(self, mon):
        """Erstellt die Layer-Shell-Surface für den spezifischen Monitor."""
        mon.surface = self.compositor.create_surface()
        # Layer-Surface an den spezifischen wl_output binden
        mon.layer_surface = self.layer_shell.get_layer_surface(
            mon.surface, mon.wl_output, 1, "desktop_icons"
        )
        mon.layer_surface.set_size(mon.width, mon.height)
        mon.layer_surface.set_anchor(15) # Top + Bottom + Left + Right (Full Screen)
        
        # Buffer-Initialisierung
        mon.setup_buffer(self.shm)
        mon.surface.commit()
        self.display.flush()
        
        # Initialer Render-Vorgang für diesen Monitor
        self.render_monitor(mon)

    def load_positions(self):
        """Lädt die Grid-Positionen der Icons aus der JSON-Datei."""
        if os.path.exists(self.pos_file):
            try:
                with open(self.pos_file, 'r') as f:
                    self.icon_positions = json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der Positionen: {e}")

    def render_monitor(self, mon):
        """Zeichnet alle Icons, die diesem Monitor-Namen zugeordnet sind."""
        # Transparentes Bild erstellen
        img = Image.new('RGBA', (mon.width, mon.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Icons filtern und zeichnen
        for filename, pos in self.icon_positions.items():
            if pos.get('monitor') == mon.name:
                gx, gy = pos['grid_x'], pos['grid_y']
                
                # Umrechnung: Grid-Koordinate -> Pixel-Koordinate
                px = gx * self.grid_size + (self.grid_size - self.icon_size) // 2
                py = gy * self.grid_size + 10
                
                # Platzhalter für das Icon (Hier später echte Icon-Logik einfügen)
                draw.rectangle([px, py, px+self.icon_size, py+self.icon_size], fill=(0, 120, 215, 200))
                draw.text((px, py + self.icon_size + 5), filename[:12], fill="white")

        # Pixeldaten in Shared Memory schreiben
        mon.shm_data.seek(0)
        mon.shm_data.write(img.tobytes())
        
        # Surface aktualisieren
        mon.surface.attach(mon.buffer, 0, 0)
        mon.surface.damage(0, 0, mon.width, mon.height)
        mon.surface.commit()
        self.display.flush()

    def run(self):
        """Hauptschleife des Programms."""
        print("🚀 LD-Icons Multi-Monitor Modus aktiv. Drücke Strg+C zum Beenden.")
        try:
            while True:
                self.display.dispatch(block=True)
        except KeyboardInterrupt:
            print("\nBeende LD-Icons...")

if __name__ == "__main__":
    app = LDIcons()
    
    # Erste Synchronisation mit dem Server
    app.display.roundtrip()
    
    # Haupt-Loop
    app.run()