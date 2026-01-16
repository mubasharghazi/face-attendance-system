"""
GUI Package
Contains all GUI modules for the Face Attendance System.
"""

from gui.main_window import MainWindow
from gui.dashboard_tab import DashboardTab
from gui.register_tab import RegisterTab
from gui.attendance_tab import AttendanceTab
from gui.records_tab import RecordsTab
from gui.reports_tab import ReportsTab
from gui.settings_tab import SettingsTab

__all__ = [
    'MainWindow',
    'DashboardTab',
    'RegisterTab',
    'AttendanceTab',
    'RecordsTab',
    'ReportsTab',
    'SettingsTab'
]
