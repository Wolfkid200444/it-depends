import unittest

from it_depends import Dependency, DependencyRecursionError, Package, resolve


class ResolveRecursionTests(unittest.TestCase):
    def test_self_dependency_off_by_one_raises_explaining_error(self) -> None:
        def provider(dep: Dependency) -> Package:
            return Package(dep.name, dep.version).with_dependencies(
                [Dependency(dep.name, dep.version + 1)]
            )

        with self.assertRaisesRegex(
            DependencyRecursionError,
            r"Recursive dependency detected.*it-depends@2.*it-depends@1 -> it-depends@2",
        ):
            resolve(Dependency("it-depends", 1), provider)

    def test_non_recursive_dependency_resolves(self) -> None:
        def provider(dep: Dependency) -> Package:
            if dep.name == "a":
                return Package("a", dep.version).with_dependencies([Dependency("b", 1)])
            return Package(dep.name, dep.version)

        resolved = resolve(Dependency("a", 1), provider)
        self.assertEqual([("a", 1), ("b", 1)], [(p.name, p.version) for p in resolved])


if __name__ == "__main__":
    unittest.main()
