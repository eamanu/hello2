from __future__ import annotations

from dagger import function, object_type, check
from dagger_clients.core import Container, Directory, Workspace, core


@object_type
class Ci:
    source: Directory
    base_image_address: str

    @classmethod
    def create(
        cls,
        ws: Workspace,
        base_image_address: str = "ghcr.io/astral-sh/uv:python3.13-trixie-slim",
    ) -> Ci:
        return cls(
            source=ws.directory(
                "/",
                exclude=[
                    "**/.dagger",
                    "**/.git",
                ],
                gitignore=True,
            ),
            base_image_address=base_image_address,
        )

    @function
    def container(self) -> Container:
        """A container with the workspace source, ready to build."""
        return (
            core()
            .container()
            .from_(self.base_image_address)
            .with_directory("/src", self.source)
            .with_workdir("/src")
        )

    @function
    async def hello(self) -> str:
        return await self.container().with_exec(["uv", "run", "hello"]).stdout()

    @function
    @check
    async def lint(self) -> None:
        await self.container().with_exec(["uv", "run", "ruff", "check", "."]).sync()

    @function
    @check
    async def tests(self) -> None:
        await self.container().with_exec(["uv", "run", "pytest"]).sync()
