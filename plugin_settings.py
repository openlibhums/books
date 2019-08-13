PLUGIN_NAME = 'Books Plugin'
DESCRIPTION = 'This plugin supports the publication of books in Janeway.'
AUTHOR = 'Andy Byers'
VERSION = '1.1'
SHORT_NAME = 'books'
MANAGER_URL = 'books_admin'
JANEWAY_VERSION = "1.3.5"


from utils import models


def install():
    new_plugin, created = models.Plugin.objects.get_or_create(name=SHORT_NAME, version=VERSION, enabled=True,
                                                              press_wide=True)

    if created:
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        print('Plugin {0} is already installed.'.format(PLUGIN_NAME))


def hook_registry():
    # On site load, the load function is run for each installed plugin to generate
    # a list of hooks.
    pass
