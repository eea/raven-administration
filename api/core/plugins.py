import os
import importlib
import logging

logger = logging.getLogger(__name__)


class Plugins:
    def init_app(self, app):
        plugins_dir = os.path.join(os.path.dirname(__file__), '../plugins')
        if not os.path.isdir(plugins_dir):
            logger.info('No plugins directory found, skipping plugin loading')
            return

        for name in sorted(os.listdir(plugins_dir)):
            plugin_path = os.path.join(plugins_dir, name)
            init_file = os.path.join(plugin_path, '__init__.py')
            if not os.path.isdir(plugin_path) or not os.path.isfile(init_file):
                continue
            try:
                module = importlib.import_module(f'plugins.{name}')
                if hasattr(module, 'register'):
                    module.register(app)
                    logger.info(f'Plugin loaded: {name}')
                else:
                    logger.warning(f'Plugin {name} has no register() function, skipping')
            except Exception as e:
                logger.error(f'Failed to load plugin {name}: {e}')
