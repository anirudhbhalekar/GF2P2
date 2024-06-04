import getopt
import sys
import os

import wx
import gettext

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui

# Initialize gettext translation
locale = "en"
if len(sys.argv) > 2:
    if sys.argv[2] == "el" or sys.argv[2] == "el_GR" or sys.argv[2] == "el_GR.utf8":
        locale = "el_GR.utf8"
        print("Locale: Ελληνικα")
    elif sys.argv[2] == "en" or sys.argv[2] == "en_GB" or sys.argv[2] == "en_GB.utf8":
        print("Locale: English")
    else:
        print("Locale unknown, defaulting to English")
lang = gettext.translation("logsim", localedir=os.path.join(os.path.dirname(__file__), 'locales'), languages=[locale], fallback=True)
lang.install()
_ = lang.gettext

def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = _("""Usage:
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>""")
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print(_("Error: invalid command line arguments\n"))
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            scanner = Scanner(path, names)
            parser = Parser(names, devices, network, monitors, scanner)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()

    if not options:  # no option given, use the graphical user interface

        if len(arguments) > 2:  # wrong number of arguments
            print(_("Error: one file path required and one language code optional\n"))
            print(usage_message)
            sys.exit()

        path = arguments[0]
        scanner = Scanner(path, names)
        parser = Parser(names, devices, network, monitors, scanner)
        
        assert parser.parse_network()
        # Initialise an instance of the gui.Gui() class
        app = wx.App()
        gui = Gui(_("Logic Simulator"), path, names, devices, network,
                    monitors)
        gui.Show(True)
        app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
