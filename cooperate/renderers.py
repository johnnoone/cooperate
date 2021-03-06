import yaml

__all__ = ['Renderer', 'StatusRenderer']


class Renderer:
    pass


class StatusRenderer(Renderer):

    def render(self, future, node, command):
        try:
            result = future.result()
            response = {
                'node': node.name,
                'command': command,
                'stdout': result.stdout or None,
                'stderr': result.stderr or None,
                'code': result.code,
                'error': result.error or None,
            }
        except Exception as error:
            response = {
                'node': node.name,
                'command': command,
                'stdout': None,
                'stderr': None,
                'code': None,
                'error': str(error)
            }

        return yaml.dump(response,
                         explicit_start=True,
                         default_flow_style=False)
