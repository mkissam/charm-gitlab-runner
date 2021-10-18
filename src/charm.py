#!/usr/bin/env python3
# Copyright 2021 Márton Kiss
# See LICENSE file for licensing details.

import logging
import os
import subprocess
from subprocess import check_call, check_output

from charmhelpers.fetch import (
    apt_install, add_source, apt_update, add_source)

from ops.charm import CharmBase
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    MaintenanceStatus,
)
from ops.framework import StoredState

logger = logging.getLogger(__name__)


class GitlabRunnerCharm(CharmBase):
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.install, self.on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.fortune_action, self._on_fortune_action)
        self._stored.set_default(things=[])

    def _get_codename_from_fs(self):
        """Get Codename from /etc/os-release."""
        with open(os.path.join(os.sep, 'etc', 'os-release')) as fin:
            content = dict(
                line.split('=', 1)
                for line in fin.read().splitlines()
                if '=' in line
            )
        for k, v in content.items():
            content[k] = v.strip('"')
        return content["UBUNTU_CODENAME"]

    def install_docker_packages(self):
        logger.info("Installing docker packages")
        apt_update()
        apt_install(["apt-transport-https", "ca-certificates", "curl",
                    "gnupg", "lsb-release"])        
        curl_options = "" # proxy should go there
        docker_key_url = "https://download.docker.com/linux/ubuntu/gpg"        
        cmd = [
            "/bin/bash", "-c",
            "set -o pipefail ; curl {} "
            "-fsSL --connect-timeout 10 "
            "{} | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
            "".format(curl_options, docker_key_url)
        ]
        check_output(cmd)
        dist = self._get_codename_from_fs()
        arch = "amd64"
        docker_repo = "deb [arch={ARCH} signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu {CODE} stable"
        cmd = ("echo \"{}\" | sudo tee /etc/apt/sources.list.d/docker.list".format(docker_repo.replace("{ARCH}", arch).replace("{CODE}", dist)))
        check_output(cmd, shell=True)
        apt_update()
        apt_install(["docker-ce", "docker-ce-cli", "containerd.io"])


    def install_gitlab_runner(self):
        logger.info("Installing gitlab runner packages")

        # install gitlab key
        curl_options = ""
        gitlab_key_url = "https://packages.gitlab.com/runner/gitlab-runner/gpgkey"
        cmd = [
            "/bin/bash", "-c",
            "set -o pipefail ; curl {} "
            "-fsSL --connect-timeout 10 "
            "{} | sudo apt-key add -"
            "".format(curl_options, gitlab_key_url)
        ]
        check_output(cmd)

        # install gitlab package
        dist = self._get_codename_from_fs()
        arch = "amd64"
        docker_repo = "deb [arch={ARCH}] https://packages.gitlab.com/runner/gitlab-runner/ubuntu/ {CODE} main"
        cmd = ("echo \"{}\" | sudo tee /etc/apt/sources.list.d/runner_gitlab-runner.list".format(docker_repo.replace("{ARCH}", arch).replace("{CODE}", dist)))
        check_output(cmd, shell=True)
        apt_update()
        apt_install(["gitlab-runner"])



if __name__ == "__main__":
    main(GitlabRunnerCharm)
