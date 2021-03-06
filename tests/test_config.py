from collections.abc import Iterable

import pytest

from tests.fixtures import wow_dir_path
from tests.util import Environment
from wap.commands.common import DEFAULT_PROJECT_VERSION
from wap.exception import (
    ConfigFileException,
    ConfigSchemaException,
    ConfigSemanticException,
)


@pytest.mark.parametrize(
    ("run_args",),
    [
        [
            ("package",),
        ],
        [
            (
                "dev-install",
                "--wow-addons-path",
                # yikes, gotta put our root in front when we use pyfakefs
                # usually, we can just query env.wow_dir_path, but because this is
                # defined in parameters, we don't have access to that.
                "/" + str(wow_dir_path("retail")),
            )
        ],
        [
            (
                "upload",
                "--version",
                DEFAULT_PROJECT_VERSION,
                "--curseforge-token",
                "abc123",
            )
        ],
    ],
    ids=["package", "dev-install", "upload"],
)
class TestConfigUsingCommands:
    def test_config_path_not_file(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(project_dir_name="basic", wow_dir_name="retail")
        env.config_file_path.unlink()

        with pytest.raises(ConfigFileException, match=r"No such config file"):
            env.run_wap(*run_args)

    def test_config_wow_version_bad_format(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="version_bad_format",
            wow_dir_name="retail",
        )

        with pytest.raises(
            ConfigSemanticException, match=r"WoW versions must be of form"
        ):
            env.run_wap(*run_args)

    def test_config_dir_paths_not_unique(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="dir_paths_not_unique",
            wow_dir_name="retail",
        )

        with pytest.raises(ConfigSemanticException, match=r"must have unique paths"):
            env.run_wap(*run_args)

    @pytest.mark.parametrize(
        ("config_file_name"),
        [
            "version_too_many_classic",
            "version_too_many_retail",
            "version_duplicated_version",
        ],
    )
    def test_config_version_too_many_of_same_type(
        self, env: Environment, config_file_name: str, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name=config_file_name,
            wow_dir_name="retail",
        )

        with pytest.raises(ConfigSemanticException, match=r"at most one \w+ version"):
            env.run_wap(*run_args)

    def test_config_does_not_follow_schema(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="does_not_follow_schema",
            wow_dir_name="retail",
        )

        with pytest.raises(ConfigSchemaException):
            env.run_wap(*run_args)

    def test_config_curseforge_changelog_not_relative(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="curseforge_changelog_not_relative",
            wow_dir_name="retail",
        )

        with pytest.raises(ConfigSemanticException, match=r"must be relative"):
            env.run_wap(*run_args)

    def test_config_dir_path_not_relative(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="dir_path_not_relative",
            wow_dir_name="retail",
        )

        with pytest.raises(ConfigSemanticException, match=r"must be relative"):
            env.run_wap(*run_args)

    def test_config_toc_file_not_relative(
        self, env: Environment, run_args: Iterable[str]
    ) -> None:
        env.prepare(
            project_dir_name="basic",
            config_file_name="toc_file_not_relative",
            wow_dir_name="retail",
        )

        with pytest.raises(ConfigSemanticException, match=r"must be relative"):
            env.run_wap(*run_args)


def test_commands_config_no_curseforge_required(env: Environment) -> None:
    # curseforge section is optional for package and dev-install
    env.prepare(
        project_dir_name="basic",
        config_file_name="no_curseforge",
        wow_dir_name="retail",
    )

    env.run_wap("package")
    env.run_wap("dev-install", "--wow-addons-path", str(env.wow_dir_path))
