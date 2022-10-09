from PySide6.QtWidgets import QDialog, QMessageBox


class CustomDialog(QDialog):
    """
    Custom QDialog class that enables the possibility to properly produce
    a message box in the component editor to the users,
    asking if they are sure to quit editing component when exiting.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_accepting_component = True

    def disable_msg_box(self):
        self._is_accepting_component = False

    def close_without_msg_box(self):
        """
        Close widget without producing the message box in closeEvent method.
        """
        self.disable_msg_box()
        self.close()

    def closeEvent(self, event):
        """
        Overriding closeEvent function in the superclass to produce a message box prompting
        the user to exit the add/edit component window. This message box pops up
        when the user exits by pressing the window close (X) button.
        """
        if not self._is_accepting_component:
            event.accept()
            return
        quit_msg = "Do you want to close the group editor?"
        reply = QMessageBox.question(
            self,
            "Really quit?",
            quit_msg,
            QMessageBox.Close | QMessageBox.Ignore,
            QMessageBox.Close,
        )
        if reply == QMessageBox.Close:
            event.accept()
        else:
            event.ignore()
