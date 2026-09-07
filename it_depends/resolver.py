from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class Dependency:
    name: str
    version: int


@dataclass(frozen=True)
class Package:
    name: str
    version: int
    dependencies: tuple[Dependency, ...] = ()

    def with_dependencies(self, dependencies: Iterable[Dependency]) -> Package:
        return Package(self.name, self.version, tuple(dependencies))


class DependencyRecursionError(ValueError):
    pass


def resolve(root: Dependency, package_provider: Callable[[Dependency], Package]) -> list[Package]:
    resolved: list[Package] = []
    seen: set[Dependency] = set()

    def _resolve(dep: Dependency, stack: tuple[Package, ...]) -> None:
        package = package_provider(dep)
        if package.name in {ancestor.name for ancestor in stack}:
            trail = " -> ".join(f"{p.name}@{p.version}" for p in (*stack, package))
            raise DependencyRecursionError(
                f"Recursive dependency detected for {package.name}@{package.version}: {trail}"
            )
        if dep in seen:
            return
        seen.add(dep)
        resolved.append(package)
        for dependency in package.dependencies:
            _resolve(dependency, (*stack, package))

    _resolve(root, ())
    return resolved
