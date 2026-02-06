#!/usr/bin/env python3
"""
System Profiler - Rilevamento automatico capacità sistema

Rileva RAM, CPU e imposta timeout/limiti dinamici per prevenire
blocchi del sistema quando le risorse sono limitate.

Autore: Carlo
Versione: 1.0.0
"""

import os
import sys
import platform
import threading
import time
from typing import Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Psutil per info sistema (opzionale ma consigliato)
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class SystemTier(Enum):
    """Categorie di potenza del sistema."""
    MINIMAL = "minimal"    # RAM < 4GB - Modalità sopravvivenza
    LOW = "low"            # RAM 4-8GB - Timeout brevi
    MEDIUM = "medium"      # RAM 8-16GB - Timeout normali
    HIGH = "high"          # RAM >= 16GB - Nessun limite


@dataclass
class SystemProfile:
    """Profilo delle capacità del sistema."""
    tier: SystemTier
    ram_total_gb: float
    ram_available_gb: float
    ram_percent_used: float
    cpu_cores: int
    cpu_percent: float
    has_gpu: bool

    # Timeout dinamici (in secondi)
    timeout_tts: int
    timeout_llm: int
    timeout_image: int
    timeout_document: int

    # Limiti operazioni
    max_parallel_ops: int
    max_text_length: int

    # Soglie di allarme
    ram_warning_threshold: float  # % RAM oltre cui avvisare
    ram_critical_threshold: float  # % RAM oltre cui bloccare nuove operazioni

    # Info dettagliate (con default per retrocompatibilita')
    gpu_name: str = ""
    gpu_vram_gb: float = 0.0
    cpu_name: str = ""


# ============================================================================
# CONFIGURAZIONE PER TIER
# ============================================================================

TIER_CONFIGS = {
    SystemTier.MINIMAL: {
        "timeout_tts": 15,
        "timeout_llm": 30,
        "timeout_image": 20,
        "timeout_document": 15,
        "max_parallel_ops": 1,
        "max_text_length": 500,
        "ram_warning_threshold": 70,
        "ram_critical_threshold": 85,
    },
    SystemTier.LOW: {
        "timeout_tts": 30,
        "timeout_llm": 60,
        "timeout_image": 45,
        "timeout_document": 30,
        "max_parallel_ops": 2,
        "max_text_length": 2000,
        "ram_warning_threshold": 75,
        "ram_critical_threshold": 90,
    },
    SystemTier.MEDIUM: {
        "timeout_tts": 60,
        "timeout_llm": 120,
        "timeout_image": 90,
        "timeout_document": 60,
        "max_parallel_ops": 4,
        "max_text_length": 10000,
        "ram_warning_threshold": 80,
        "ram_critical_threshold": 92,
    },
    SystemTier.HIGH: {
        "timeout_tts": 120,
        "timeout_llm": 300,
        "timeout_image": 180,
        "timeout_document": 120,
        "max_parallel_ops": 8,
        "max_text_length": 50000,
        "ram_warning_threshold": 85,
        "ram_critical_threshold": 95,
    },
}


# ============================================================================
# RILEVAMENTO SISTEMA
# ============================================================================

def get_ram_info() -> Tuple[float, float, float]:
    """
    Ritorna (ram_total_gb, ram_available_gb, ram_percent_used).
    """
    if HAS_PSUTIL:
        mem = psutil.virtual_memory()
        return (
            mem.total / (1024**3),
            mem.available / (1024**3),
            mem.percent
        )

    # Fallback Linux: leggi /proc/meminfo
    if platform.system() == "Linux":
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = {}
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0].rstrip(":")
                        value = int(parts[1]) / (1024**2)  # KB -> GB
                        meminfo[key] = value

                total = meminfo.get("MemTotal", 4)
                available = meminfo.get("MemAvailable", meminfo.get("MemFree", 2))
                percent = ((total - available) / total) * 100 if total > 0 else 50
                return (total, available, percent)
        except:
            pass

    # Fallback Windows
    if platform.system() == "Windows":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            c_ulonglong = ctypes.c_ulonglong

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ('dwLength', ctypes.c_ulong),
                    ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', c_ulonglong),
                    ('ullAvailPhys', c_ulonglong),
                    ('ullTotalPageFile', c_ulonglong),
                    ('ullAvailPageFile', c_ulonglong),
                    ('ullTotalVirtual', c_ulonglong),
                    ('ullAvailVirtual', c_ulonglong),
                    ('ullAvailExtendedVirtual', c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

            total = stat.ullTotalPhys / (1024**3)
            available = stat.ullAvailPhys / (1024**3)
            percent = stat.dwMemoryLoad
            return (total, available, percent)
        except:
            pass

    # Default conservativo
    return (4.0, 2.0, 50.0)


def get_cpu_info() -> Tuple[int, float]:
    """
    Ritorna (cpu_cores, cpu_percent).
    """
    cores = os.cpu_count() or 2

    if HAS_PSUTIL:
        try:
            percent = psutil.cpu_percent(interval=0.1)
            return (cores, percent)
        except:
            pass

    return (cores, 0.0)


def detect_gpu() -> Tuple[bool, str, float]:
    """Rileva GPU, nome e VRAM. Ritorna (has_gpu, gpu_name, gpu_vram_gb)."""
    # Controlla NVIDIA
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            line = result.stdout.strip().split('\n')[0]
            parts = [p.strip() for p in line.split(',')]
            gpu_name = parts[0] if parts else "NVIDIA GPU"
            gpu_vram_mb = float(parts[1]) if len(parts) > 1 else 0
            gpu_vram_gb = round(gpu_vram_mb / 1024, 1)
            return (True, gpu_name, gpu_vram_gb)
    except:
        pass

    # Controlla AMD ROCm
    try:
        if os.path.exists("/opt/rocm"):
            return (True, "AMD ROCm GPU", 0.0)
    except:
        pass

    return (False, "", 0.0)


def get_cpu_name() -> str:
    """Rileva il nome della CPU."""
    try:
        if platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        elif platform.system() == "Windows":
            return platform.processor() or "CPU"
        elif platform.system() == "Darwin":
            import subprocess
            result = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                    capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                return result.stdout.strip()
    except:
        pass
    return f"{os.cpu_count() or '?'} core CPU"


def determine_tier(ram_total_gb: float, ram_available_gb: float, cpu_cores: int) -> SystemTier:
    """Determina il tier del sistema basandosi sulle risorse."""

    # La RAM disponibile è più importante della RAM totale
    effective_ram = min(ram_total_gb, ram_available_gb * 2)

    if effective_ram < 4 or ram_available_gb < 1.5:
        return SystemTier.MINIMAL
    elif effective_ram < 8 or ram_available_gb < 3:
        return SystemTier.LOW
    elif effective_ram < 16 or ram_available_gb < 6:
        return SystemTier.MEDIUM
    else:
        return SystemTier.HIGH


def get_system_profile(force_tier: Optional[SystemTier] = None) -> SystemProfile:
    """
    Rileva le capacità del sistema e crea un profilo.

    Args:
        force_tier: Se specificato, usa questo tier invece di auto-rilevare
    """
    ram_total, ram_available, ram_percent = get_ram_info()
    cpu_cores, cpu_percent = get_cpu_info()
    has_gpu, gpu_name, gpu_vram_gb = detect_gpu()
    cpu_name = get_cpu_name()

    if force_tier:
        tier = force_tier
    else:
        tier = determine_tier(ram_total, ram_available, cpu_cores)

    config = TIER_CONFIGS[tier]

    return SystemProfile(
        tier=tier,
        ram_total_gb=round(ram_total, 2),
        ram_available_gb=round(ram_available, 2),
        ram_percent_used=round(ram_percent, 1),
        cpu_cores=cpu_cores,
        cpu_percent=round(cpu_percent, 1),
        has_gpu=has_gpu,
        gpu_name=gpu_name,
        gpu_vram_gb=gpu_vram_gb,
        cpu_name=cpu_name,
        **config
    )


# ============================================================================
# MEMORY WATCHDOG
# ============================================================================

class MemoryWatchdog:
    """
    Monitora la memoria e può interrompere operazioni se sta per esaurirsi.
    """

    def __init__(self, profile: SystemProfile, check_interval: float = 2.0):
        self.profile = profile
        self.check_interval = check_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: list = []
        self._blocked = False
        self._last_warning_time = 0

    def add_callback(self, callback: Callable[[str, float], None]):
        """
        Aggiunge callback chiamato quando la memoria supera le soglie.
        callback(level: "warning"|"critical", ram_percent: float)
        """
        self._callbacks.append(callback)

    def is_blocked(self) -> bool:
        """Ritorna True se nuove operazioni dovrebbero essere bloccate."""
        return self._blocked

    def start(self):
        """Avvia il monitoraggio in background."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Ferma il monitoraggio."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)

    def _monitor_loop(self):
        """Loop principale di monitoraggio."""
        while self._running:
            try:
                _, ram_available, ram_percent = get_ram_info()

                # Aggiorna lo stato di blocco
                if ram_percent >= self.profile.ram_critical_threshold:
                    self._blocked = True
                    self._notify("critical", ram_percent)
                elif ram_percent >= self.profile.ram_warning_threshold:
                    self._blocked = False
                    # Avvisa max ogni 30 secondi
                    if time.time() - self._last_warning_time > 30:
                        self._notify("warning", ram_percent)
                        self._last_warning_time = time.time()
                else:
                    self._blocked = False

            except Exception as e:
                print(f"[MemoryWatchdog] Errore: {e}")

            time.sleep(self.check_interval)

    def _notify(self, level: str, ram_percent: float):
        """Notifica tutti i callback."""
        for cb in self._callbacks:
            try:
                cb(level, ram_percent)
            except Exception as e:
                print(f"[MemoryWatchdog] Callback error: {e}")


# ============================================================================
# TIMEOUT EXECUTOR
# ============================================================================

class TimeoutError(Exception):
    """Operazione terminata per timeout."""
    pass


class MemoryError(Exception):
    """Operazione bloccata per memoria insufficiente."""
    pass


def run_with_timeout(func: Callable, timeout: float, *args, **kwargs):
    """
    Esegue una funzione con timeout.

    Raises:
        TimeoutError: Se l'operazione supera il timeout
    """
    result = [None]
    error = [None]

    def worker():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        # Il thread è ancora in esecuzione - timeout
        raise TimeoutError(f"Operazione interrotta dopo {timeout}s")

    if error[0]:
        raise error[0]

    return result[0]


def run_with_protection(
    func: Callable,
    profile: SystemProfile,
    watchdog: Optional[MemoryWatchdog] = None,
    operation_type: str = "llm",
    *args, **kwargs
):
    """
    Esegue una funzione con protezione timeout e memoria.

    Args:
        func: Funzione da eseguire
        profile: Profilo sistema per timeout
        watchdog: MemoryWatchdog opzionale
        operation_type: "tts", "llm", "image", "document"
    """
    # Controlla se le operazioni sono bloccate
    if watchdog and watchdog.is_blocked():
        raise MemoryError(
            f"Memoria insufficiente ({profile.ram_percent_used:.1f}% usata). "
            "Chiudi altre applicazioni e riprova."
        )

    # Determina timeout
    timeout_map = {
        "tts": profile.timeout_tts,
        "llm": profile.timeout_llm,
        "image": profile.timeout_image,
        "document": profile.timeout_document,
    }
    timeout = timeout_map.get(operation_type, profile.timeout_llm)

    return run_with_timeout(func, timeout, *args, **kwargs)


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_profile: Optional[SystemProfile] = None
_watchdog: Optional[MemoryWatchdog] = None


def init_system_protection(force_tier: Optional[SystemTier] = None, start_watchdog: bool = True):
    """
    Inizializza il sistema di protezione.
    Chiamare all'avvio dell'applicazione.
    """
    global _profile, _watchdog

    _profile = get_system_profile(force_tier)

    if start_watchdog:
        _watchdog = MemoryWatchdog(_profile)
        _watchdog.start()

    return _profile


def get_profile() -> SystemProfile:
    """Ritorna il profilo sistema (inizializza se necessario)."""
    global _profile
    if _profile is None:
        _profile = get_system_profile()
    return _profile


def get_watchdog() -> Optional[MemoryWatchdog]:
    """Ritorna il watchdog memoria."""
    return _watchdog


def protected_call(func: Callable, operation_type: str = "llm", *args, **kwargs):
    """
    Wrapper conveniente per chiamate protette.

    Esempio:
        result = protected_call(my_function, "tts", arg1, arg2, kwarg=value)
    """
    profile = get_profile()
    return run_with_protection(func, profile, _watchdog, operation_type, *args, **kwargs)


# ============================================================================
# CLI / TEST
# ============================================================================

def print_system_info():
    """Stampa informazioni sul sistema."""
    profile = get_system_profile()

    tier_colors = {
        SystemTier.MINIMAL: "\033[91m",  # Rosso
        SystemTier.LOW: "\033[93m",       # Giallo
        SystemTier.MEDIUM: "\033[92m",    # Verde
        SystemTier.HIGH: "\033[94m",      # Blu
    }
    reset = "\033[0m"
    color = tier_colors.get(profile.tier, "")

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║              SYSTEM PROFILER - Rilevamento Sistema           ║
╠══════════════════════════════════════════════════════════════╣
║  RAM Totale:      {profile.ram_total_gb:>6.2f} GB                             ║
║  RAM Disponibile: {profile.ram_available_gb:>6.2f} GB                             ║
║  RAM Usata:       {profile.ram_percent_used:>6.1f} %                              ║
║  CPU Cores:       {profile.cpu_cores:>6d}                                  ║
║  GPU Rilevata:    {'SI' if profile.has_gpu else 'NO':>6s}                                  ║
╠══════════════════════════════════════════════════════════════╣
║  TIER SISTEMA:    {color}{profile.tier.value.upper():>8s}{reset}                              ║
╠══════════════════════════════════════════════════════════════╣
║  Timeout TTS:     {profile.timeout_tts:>6d} sec                             ║
║  Timeout LLM:     {profile.timeout_llm:>6d} sec                             ║
║  Timeout Image:   {profile.timeout_image:>6d} sec                             ║
║  Max Parallel:    {profile.max_parallel_ops:>6d}                                  ║
║  Max Text Len:    {profile.max_text_length:>6d} chars                           ║
╠══════════════════════════════════════════════════════════════╣
║  RAM Warning:     {profile.ram_warning_threshold:>6.0f} %                              ║
║  RAM Critical:    {profile.ram_critical_threshold:>6.0f} %                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Suggerimenti
    if profile.tier == SystemTier.MINIMAL:
        print("⚠️  ATTENZIONE: Sistema con risorse molto limitate!")
        print("   - Chiudi altre applicazioni prima di usare LLM")
        print("   - Usa modelli piccoli (es. qwen2.5:1.5b)")
        print("   - Evita operazioni parallele")
    elif profile.tier == SystemTier.LOW:
        print("💡 SUGGERIMENTO: Sistema con risorse limitate")
        print("   - Preferisci modelli leggeri (es. qwen2.5:3b)")
        print("   - I timeout sono ridotti per prevenire blocchi")
    elif profile.tier == SystemTier.MEDIUM:
        print("✅ Sistema con risorse adeguate")
        print("   - Puoi usare modelli medi (es. qwen2.5:7b)")
    else:
        print("🚀 Sistema potente!")
        print("   - Puoi usare modelli grandi senza problemi")

    return profile


if __name__ == "__main__":
    print_system_info()
