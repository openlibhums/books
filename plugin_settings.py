PLUGIN_NAME = 'Books Plugin'
DESCRIPTION = 'This plugin supports the publication of books in Janeway.'
AUTHOR = 'Andy Byers'
VERSION = '1.2'
SHORT_NAME = 'books'
MANAGER_URL = 'books_admin'
JANEWAY_VERSION = "1.3.5"

from utils import models


def install():
    new_plugin, created = models.Plugin.objects.get_or_create(
        name=SHORT_NAME,
        enabled=True,
        press_wide=True,
        defaults={'version': VERSION},
    )

    if created:
        print('Plugin {0} installed.'.format(PLUGIN_NAME))
    else:
        print('Plugin {0} is already installed.'.format(PLUGIN_NAME))


def hook_registry():
    return {
        'press_admin_nav_block': {'module': 'plugins.books.hooks', 'function': 'nav_hook'}
    }

