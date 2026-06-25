"""
Public window — what the audience sees in Zoom.
Renders ONLY the slide half. Notes are never reachable from here.
Auto-hide close button appears when cursor moves to the top edge.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QColor, QCursor, QFont, QPainterPath, QLinearGradient, QPen
from PySide6.QtWidgets import QWidget, QPushButton


class _CloseButton(QPushButton):
    """Floating ✕ button that fades in/out over the fullscreen slide."""

    def __init__(self, parent: QWidget, controller):
        super().__init__("✕", parent)
        self.controller = controller
        self.setFixedSize(52, 52)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Quitter le plein écran (Esc)")
        self.setStyleSheet("""
            QPushButton {
                background: rgba(220, 50, 50, 0.92);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.30);
                border-radius: 26px;
                font-size: 20px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: rgba(255, 60, 60, 1.0);
                border: 2px solid rgba(255, 255, 255, 0.60);
            }
            QPushButton:pressed {
                background: rgba(180, 40, 40, 1.0);
            }
        """)
        self.setWindowOpacity(0)
        self.hide()
        self.clicked.connect(self._on_click)

        # opacity animation
        self._opacity = 0.0

    def _on_click(self):
        self.controller.toggle_public_fullscreen()

    def set_opacity(self, v: float):
        self._opacity = max(0.0, min(1.0, v))
        alpha = int(self._opacity * 255)
        bg_a  = int(0.92 * self._opacity * 255)
        border_a = int(0.30 * self._opacity * 255)
        border_hover_a = int(0.60 * self._opacity * 255)
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba(220, 50, 50, {bg_a});
                color: rgba(255,255,255,{alpha});
                border: 2px solid rgba(255, 255, 255, {border_a});
                border-radius: 26px;
                font-size: 20px;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background: rgba(255, 60, 60, {min(255, bg_a + 20)});
                border: 2px solid rgba(255, 255, 255, {border_hover_a});
            }}
            QPushButton:pressed {{
                background: rgba(180, 40, 40, {min(255, bg_a + 10)});
            }}
        """)
        self.setVisible(self._opacity > 0.01)


class PublicWindow(QWidget):
    HIDE_ZONE_HEIGHT = 120   # px from top where cursor triggers the button

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Présentation (à partager dans Zoom)")
        self.setStyleSheet("background:#000;")
        self.setAutoFillBackground(True)
        self._pixmap = None
        self.resize(1280, 720)

        # ── floating close button ──
        self._close_btn = _CloseButton(self, controller)
        self._opacity   = 0.0   # current opacity
        self._target    = 0.0   # target opacity

        # smooth fade timer
        self._fade_timer = QTimer(self)
        self._fade_timer.setInterval(12)   # ~83 fps for smoother animation
        self._fade_timer.timeout.connect(self._tick_fade)

        # hide-after-idle timer
        self._idle_timer = QTimer(self)
        self._idle_timer.setSingleShot(True)
        self._idle_timer.setInterval(2500)  # 2.5 s before hiding
        self._idle_timer.timeout.connect(self._hide_button)

        # track mouse only when fullscreen
        self.setMouseTracking(True)

    # ── slide rendering ─────────────────────────────────────────────────

    def set_slide(self, pixmap):
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, _ev):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0))
        if self._pixmap is None or self._pixmap.isNull():
            return
        dpr = self.devicePixelRatioF()
        pm = self.controller.render_slide_for(self.width(), self.height(), dpr)
        if pm is None or pm.isNull():
            pm = self._pixmap
        w = int(pm.width() / pm.devicePixelRatio())
        h = int(pm.height() / pm.devicePixelRatio())
        x = (self.width() - w) // 2
        y = (self.height() - h) // 2
        p.drawPixmap(x, y, pm)

    def keyPressEvent(self, ev):
        self.controller.handle_key(ev)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.controller.request_redraw()
        self._reposition_button()

    # ── close button logic ───────────────────────────────────────────────

    def _reposition_button(self):
        """Keep the ✕ button in the top-right corner."""
        margin = 24
        self._close_btn.move(self.width() - 52 - margin, margin)

    def mouseMoveEvent(self, ev):
        super().mouseMoveEvent(ev)
        if not self.isFullScreen():
            return
        y = ev.position().y() if hasattr(ev, "position") else ev.y()
        if y <= self.HIDE_ZONE_HEIGHT:
            self._show_button()
        else:
            self._idle_timer.start()   # restart idle countdown

    def _show_button(self):
        self._idle_timer.stop()
        self._target = 1.0
        if not self._fade_timer.isActive():
            self._fade_timer.start()

    def _hide_button(self):
        self._target = 0.0
        if not self._fade_timer.isActive():
            self._fade_timer.start()

    def _tick_fade(self):
        step = 0.12
        if abs(self._opacity - self._target) < step:
            self._opacity = self._target
            self._fade_timer.stop()
        elif self._opacity < self._target:
            self._opacity += step
        else:
            self._opacity -= step
        self._close_btn.set_opacity(self._opacity)

    # ── fullscreen state transitions ─────────────────────────────────────

    def changeEvent(self, ev):
        super().changeEvent(ev)
        from PySide6.QtCore import QEvent
        if ev.type() == QEvent.WindowStateChange:
            if not self.isFullScreen():
                # exiting fullscreen → hide button immediately
                self._target = 0.0
                self._opacity = 0.0
                self._close_btn.set_opacity(0.0)
                self._idle_timer.stop()
                self._fade_timer.stop()
