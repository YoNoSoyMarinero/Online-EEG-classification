from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath, QPainterPathStroker
from PyQt5.QtWidgets import QWidget

class RectangleWidget(QWidget):
    def __init__(self, parent=None, right=True):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.color = QColor(30, 30, 30, 100)
        self.right = right

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set the brush and pen for drawing the rectangle
        brush_color = self.color
        pen_color = QColor(0, 0, 0)  # Black color
        pen_width = 2

        # Set the brush and pen on the painter
        painter.setBrush(brush_color)
        painter.setPen(QPen(pen_color, pen_width))

        # Draw the rectangle using the painter
        painter.drawRect(self.rect())
        if self.right:
            arrow_path = QPainterPath()
            arrow_path.moveTo(QPointF(self.width() * 0.25, self.height() * 0.5))
            arrow_path.lineTo(QPointF(self.width() * 0.75, self.height() * 0.5))
            arrow_path.lineTo(QPointF(self.width() * 0.75, self.height() * 0.25))
            arrow_path.lineTo(QPointF(self.width() * 0.9, self.height() * 0.5))
            arrow_path.lineTo(QPointF(self.width() * 0.75, self.height() * 0.75))
            arrow_path.lineTo(QPointF(self.width() * 0.75, self.height() * 0.5))
            arrow_path.closeSubpath()
        
        else:
            arrow_path = QPainterPath()
            arrow_path.moveTo(QPointF(self.width() * 0.75, self.height() * 0.5))
            arrow_path.lineTo(QPointF(self.width() * 0.25, self.height() * 0.5))
            arrow_path.lineTo(QPointF(self.width() * 0.25, self.height() * 0.25))
            arrow_path.lineTo(QPointF(self.width() * 0.1, self.height() * 0.5))
            arrow_path.lineTo(QPointF(self.width() * 0.25, self.height() * 0.75))
            arrow_path.lineTo(QPointF(self.width() * 0.25, self.height() * 0.5))
            arrow_path.closeSubpath()

        # Adjust the stroke width of the arrow path
        stroker = QPainterPathStroker()
        stroker.setWidth(pen_width)
        arrow_stroked = stroker.createStroke(arrow_path)

        painter.setBrush(Qt.white)
        painter.setPen(QPen(Qt.black, pen_width))
        painter.drawPath(arrow_stroked)


    def set_color(self, color):
        self.color = color
        self.update()