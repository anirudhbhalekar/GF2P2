"""
Description:
    This script contains the implementation of a GUI application for the logic simulator.
    It includes custom classes for creating a graphical user interface, managing text input, and editing files.
    The application allows users to interact with various widgets,
    edit text content, and save changes to files.

Classes:
    - PromptedTextCtrl: A custom text control class for creating a command-line style text box.
    - TextEditor: A text editor window for editing source files.

Dependencies:
    - Python 3.x
    - wxPython library
    - gettext library

"""

import wx
import gettext
# Initialize gettext translation
gettext.install('logsim', localedir='locales')
_ = gettext.gettext


class PromptedTextCtrl(wx.TextCtrl):
    """
    PromptedTextCtrl - Custom text control with a prompt symbol '>' that prevents
    deletion of history and only allows modification of the current line.

    This class extends wx.TextCtrl to create a command-line style text box where each
    line starts with a '>' prompt. Users can only edit the current line, preventing
    deletion or modification of previous lines.

    Methods
    -------
    __init__(parent, id=wx.ID_ANY, *args, **kwargs)
        Initializes the text control with the specified parent and parameters.
    write_prompt()
        Appends a prompt symbol '>' to the text control and moves the cursor to the end.
    on_text_entered(event)
        Handles the event when the user presses Enter, adding a new prompt symbol and
        moving the cursor to the end.
    on_key_down(event)
        Handles key down events to prevent deletion of previous lines. Allows deletion
        within the current line and ensures the prompt symbol remains at the beginning.
    on_text(event)
        Handle text change events to ensure the prompt symbol is not deleted.
    """
    def __init__(self, parent, id=wx.ID_ANY, *args, **kwargs):
            """Initialise the text box."""
            # Combine the necessary styles
            style = wx.TE_PROCESS_ENTER | wx.TE_MULTILINE | wx.TE_RICH2 | wx.VSCROLL
            # Remove 'style' from kwargs if it exists to avoid conflict
            kwargs['style'] = style
            # Initialize the wx.TextCtrl with the combined styles
            super().__init__(parent, id, *args, **kwargs)
            self.write_prompt()
            self.Bind(wx.EVT_TEXT_ENTER, self.on_text_entered)
            self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
            self.Bind(wx.EVT_TEXT, self.on_text)

    def write_prompt(self):
        """Write the prompt symbol '>' and move the cursor to the end."""
        self.AppendText("> ")
        self.SetInsertionPointEnd()

    def on_text_entered(self, event):
        """Handle the event when the user enters text."""
        # Move the cursor to the end, then append the prompt
        self.AppendText("") # I have no idea why this works but don't delete it
        self.SetInsertionPointEnd()

    def on_key_down(self, event):
        """Handle key down events to prevent deletion of previous lines."""
        keycode = event.GetKeyCode()
        current_position = self.GetInsertionPoint()
        last_line_start = self.GetLastPosition() - self.GetLineLength(self.GetNumberOfLines() - 1)

        if keycode == wx.WXK_BACK:
            # Prevent deletion of the prompt symbol '>'
            if current_position > last_line_start + 2:
                event.Skip()
        elif keycode == wx.WXK_DELETE:
            # Prevent deletion of the prompt symbol '>'
            if current_position >= last_line_start + 2:
                event.Skip()
        elif keycode in (wx.WXK_UP, wx.WXK_DOWN):
            # Prevent moving the cursor to other lines
            return
        else:
            event.Skip()
    
    def on_text(self, event):
        """Handle text change events to ensure the prompt symbol is not deleted."""
        last_line = self.GetNumberOfLines() - 1
        line_text = self.GetLineText(last_line)
        
        if not line_text.startswith("> "):
            self.ChangeValue(self.GetValue()[:self.GetLastPosition() - len(line_text)] + "> " + line_text[2:])
            self.SetInsertionPointEnd()

class TextEditor(wx.Frame):
    """
    TextEditor - Text editor window for editing source files.

    This class provides a graphical interface for editing source files. It allows users to
    edit text content and save it to a file.

    Parameters
    ----------
    parent : wx.Window
        The parent window.
    title : str
        Title of the text editor window.
    initial_text : str, optional
        Initial text content to display in the editor.

    Methods
    -------
    get_text()
        Get text content of the text editor.
    update_text(path)
        Update the text editor with text from a file specified by the given path.
    on_save(event)
        Handle save button click event.
    """

    def __init__(self, parent, title, initial_text=""):
        """
        Initialize the text editor window.

        Parameters
        ----------
        parent : wx.Window
            The parent window.
        title : str
            Title of the text editor window.
        initial_text : str, optional
            Initial text content to display in the editor.
        """
        super().__init__(parent, title=title, size=(400, 600))
        
        # Use default text control format wx.TextCtrl
        self.text_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        # Read the current path to populate default text in editor
        with open(parent.path, 'r') as file:
            initial_text = file.read()
        self.initial_text = initial_text
        self.text_ctrl.SetValue(initial_text)
        #print(self.initial_text, "is the initial text")

        # Add a Save button
        self.save_button = wx.Button(self, label=_('Save'))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

        # Use a sizer for layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.save_button, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        # Set minimum window size and make "sizer" the sizer
        self.SetSizeHints(200, 400)
        self.SetSizer(sizer)

    def get_text(self):
        """Get text content of the text editor."""
        return self.text_ctrl.GetValue()

    def update_text(self, path):
        """Populate the Text Editor with the contents of the text file from a given path."""
        self.path = path
        with open(self.path, 'r') as file:
            initial_text = file.read()
        self.initial_text = initial_text
        self.text_ctrl.SetValue(initial_text)

    def on_save(self, event):
        """Handle save button click."""
        # Open a file dialog for the user to choose a file location
        with wx.FileDialog(self, _("Save File"), wildcard="Text files (*.txt)|*.txt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                # If the user cancels, return without saving
                return
            
            # Get the selected file path
            filepath = file_dialog.GetPath()
            
            try:
                # Open the file in write mode and write the text from the editor
                with open(filepath, 'w') as file:
                    text = self.text_ctrl.GetValue()
                    file.write(text)
            except IOError:
                # Handle any errors that occur during file saving
                wx.LogError(_("Cannot save current data to file."))