import gettext
import sys
import os
# Initialize gettext translation
locale = sys.argv[1] if len(sys.argv) > 1 else "en"
lang = gettext.translation("logsim", localedir=os.path.join(os.path.dirname(__file__), 'locales'), languages=[locale], fallback=True)
lang.install()
_ = lang.gettext

def main():
    print(_("Hello world"))

if __name__ == "__main__":
    main()