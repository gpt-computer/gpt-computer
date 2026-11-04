import gptc

from gpt_computer.infrastructure.cookies import read_cookie_files

from ..gui import run_gui
from ..Provider import ProviderLoader
from .gui_parser import gui_parser


def run_gui_args(args):
    if args.debug:
        gptc.debug.logging = True
    if not args.ignore_cookie_files:
        read_cookie_files()
    host = args.host
    port = args.port
    debug = args.debug
    gptc.cookies.BROWSERS = [gptc.cookies[browser] for browser in args.cookie_browsers]
    if args.ignored_providers:
        ProviderLoader.ignored = args.ignored_providers

    run_gui(host, port, debug)


if __name__ == "__main__":
    parser = gui_parser()
    args = parser.parse_args()
    run_gui_args(args)
