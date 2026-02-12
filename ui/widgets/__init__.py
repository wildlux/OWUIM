"""Widget package - ogni widget in file separato."""

from ui.widgets.dashboard import DashboardWidget
from ui.widgets.logs import LogsWidget
from ui.widgets.models import ModelsWidget
from ui.widgets.config_widget import ConfigWidget
from ui.widgets.tts import TTSWidget
from ui.widgets.archivio import ArchivioWidget
from ui.widgets.info import InfoWidget
from ui.widgets.mcp import MCPWidget

__all__ = [
    'DashboardWidget', 'LogsWidget', 'ModelsWidget', 'ConfigWidget',
    'TTSWidget', 'ArchivioWidget', 'InfoWidget', 'MCPWidget',
]
