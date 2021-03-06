# Licensed under a 3-clause BSD style license - see LICENSE.rst
import sys
import argparse

from glue.app.qt import GlueApplication
from glue.main import restore_session, get_splash, load_data_files, load_plugins
from qtpy.QtCore import QTimer

try:
    from glue.utils.qt.decorators import die_on_error
except ImportError:
    from glue.utils.decorators import die_on_error

from .version import version as cubeviz_version
from .data_factories import DataFactoryConfiguration


def setup():

    from . import layout  # noqa
    from . import startup  # noqa


@die_on_error("Error starting up Cubeviz")
def main(argv=sys.argv):
    """
    The majority of the code in this function was taken from start_glue() in main.py after a discussion with
    Tom Robataille. We wanted the ability to get command line arguments and use them in here and this seemed
    to be the cleanest way to do it.

    :param argv:
    :return:
    """

    # # Parse the arguments, ignore any unkonwn
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-configs", help="Directory or file for data configuration YAML files", action='append', default=[])
    parser.add_argument("--data-configs-show", help="Show the matching info", action="store_true", default=False)
    parser.add_argument('data_files', nargs=argparse.REMAINDER)
    args = parser.parse_known_args(argv[1:])

    # Store the args for each ' --data-configs' found on the commandline
    data_configs = args[0].data_configs
    data_configs_show = args[0].data_configs_show

    import glue
    from glue.utils.qt import get_qapp
    app = get_qapp()

    # Splash screen
    splash = get_splash()
    splash.show()

    # Start off by loading plugins. We need to do this before restoring
    # the session or loading the configuration since these may use existing
    # plugins.
    load_plugins(splash=splash)

    # Load the
    DataFactoryConfiguration(data_configs, data_configs_show, remove_defaults=True)

    datafiles = args[0].data_files

    # Show the splash screen for 1 second
    timer = QTimer()
    timer.setInterval(1000)
    timer.setSingleShot(True)
    timer.timeout.connect(splash.close)
    timer.start()

    data_collection = glue.core.DataCollection()
    hub = data_collection.hub

    splash.set_progress(100)

    session = glue.core.Session(data_collection=data_collection, hub=hub)
    ga = GlueApplication(session=session)

    ga.run_startup_action('cubeviz')

    # Load the data files.
    if datafiles:
        datasets = load_data_files(datafiles)
        ga.add_datasets(data_collection, datasets, auto_merge=False)

    ga.setWindowTitle('cubeviz ({})'.format(cubeviz_version))

    sys.exit(ga.start(maximized=True))
