import os
from jinja2 import Environment, FileSystemLoader
import yaml

src_folder = os.environ.get('PKG_NAME')
workspace = os.environ.get('GITHUB_WORKSPACE')

config_path = os.path.join(
    workspace, "repo", "pkgs", src_folder, "config.yml")
with open(config_path, "r") as f:
    pkg_config = yaml.safe_load(f)

if pkg_config['pkg_service']:
    if pkg_config['pkg_service']['template']:
        env = Environment(
            loader=FileSystemLoader(os.path.join(workspace, "repo", 'service_templates')))
        template = env.get_template(pkg_config['pkg_service']['template'] + ".jinja")
        service = template.render(
            pkg_config['pkg_service']['vars'] |
            {'NAME': pkg_config['pkg_manifest']['name'].lower()})
    else:
        service = pkg_config['pkg_service']['service']
    file_name = f"{pkg_config['pkg_manifest']['name'].lower()}"
    with open(file_name, 'w') as file:
        file.write(service)
    os.chmod(file_name, 0o775)