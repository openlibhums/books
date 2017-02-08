PLUGIN_NAME = 'Books Plugin'
DESCRIPTION = 'This plugin supports the publication of books in Acta.'
AUTHOR = 'Andy Byers'
VERSION = '1.0'
SHORT_NAME = 'books'

from utils import models

def install():
	new_plugin, created = models.Plugin.objects.get_or_create(name=SHORT_NAME, version=VERSION, enabled=True)

	if created:
		print('Plugin {0} installed.'.format(PLUGIN_NAME))
	else:
		print('Plugin {0} is already installed.'.format(PLUGIN_NAME))


def hook_registry():
	# On site load, the load function is run for each installed plugin to generate
	# a list of hooks.
    pass
	#return {'article_footer_block': {'module': 'plugins.disqus.hooks', 'function': 'inject_disqus'}}