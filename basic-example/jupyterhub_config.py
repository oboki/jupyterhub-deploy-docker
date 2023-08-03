# https://github.com/jupyterhub/dockerspawner/blob/main/examples/image_form/jupyterhub_config.py

import os

c = get_config()  # noqa


options_form_tpl = """
<label for="image">Image</label>
<select name="image" size="1">
    <option value="jupyter/base-notebook">base-notebook</option>
    <option value="jupyter/base-notebook-2">base-notebook-2</option>
</select>
"""


def get_options_form(spawner):
    return options_form_tpl.format(default_image=spawner.image)


c.DockerSpawner.options_form = get_options_form

from dockerspawner import DockerSpawner


class CustomDockerSpawner(DockerSpawner):
    def options_from_form(self, formdata):
        options = {}
        image_form_list = formdata.get("image", [])
        if image_form_list and image_form_list[0]:
            options["image"] = image_form_list[0].strip()
            self.log.info(f"User selected image: {options['image']}")
        return options

    def load_user_options(self, options):
        image = options.get("image")
        if image:
            self.log.info(f"Loading image {image}")
            self.image = image


c.JupyterHub.spawner_class = CustomDockerSpawner

# the rest of the config is testing boilerplate
# to make the Hub connectable from the containers

# dummy for testing. Don't use this in production!
c.JupyterHub.authenticator_class = "dummy"
# while using dummy auth, make the *public* (proxy) interface private
c.JupyterHub.ip = "0.0.0.0"

# we need the hub to listen on all ips when it is in a container
c.JupyterHub.hub_ip = "0.0.0.0"

# may need to set hub_connect_ip to be connectable to containers
# default hostname behavior usually works, though
# c.JupyterHub.hub_connect_ip

# pick a default image to use when none is specified
c.DockerSpawner.image = "jupyter/base-notebook"

# delete containers when they stop
c.DockerSpawner.remove = True

notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR", "/home/jovyan/work")
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = {"jupyterhub-user-{username}": notebook_dir}
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = "jupyterhub-network"