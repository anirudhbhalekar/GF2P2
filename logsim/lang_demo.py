import gettext
import sys
# Initialize gettext translation
locale = sys.argv[1] if len(sys.argv) > 1 else "en"
lang = gettext.translation("logsim", localedir=r'C:\Users\Shawn\Documents\Cambridge Part IIA\Project GF2\GF2P2\logsim\locales', languages=[locale], fallback=True)
lang.install()
_ = lang.gettext

def main():
    print(_("Hello world"))

if __name__ == "__main__":
    main()