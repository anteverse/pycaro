from functools import lru_cache
from pathlib import Path
from typing import Sequence, Iterable, Optional, Iterator, List

from pathspec import PathSpec
from pathspec.patterns.gitwildmatch import GitWildMatchPatternError


@lru_cache()
def find_project_root(srcs: Sequence[str]) -> Path:
    """
    COPIED FROM psf/black

    Return a directory containing .git, .hg, or pyproject.toml.
    That directory will be a common parent of all files and directories
    passed in `srcs`.
    If no directory in the tree contains a marker that would specify it's the
    project root, the root of the file system is returned.
    """
    if not srcs:
        srcs = [str(Path.cwd().resolve())]

    path_srcs = [Path(Path.cwd(), src).resolve() for src in srcs]

    # A list of lists of parents for each 'src'. 'src' is included as a
    # "parent" of itself if it is a directory
    src_parents = [
        list(path.parents) + ([path] if path.is_dir() else []) for path in path_srcs
    ]

    common_base = max(
        set.intersection(*(set(parents) for parents in src_parents)),
        key=lambda path: path.parts,
    )

    for directory in (common_base, *common_base.parents):
        if (directory / ".git").exists():
            return directory

        if (directory / ".hg").is_dir():
            return directory

        if (directory / "pyproject.toml").is_file():
            return directory

    return directory


@lru_cache()
def get_gitignore(root: Path) -> PathSpec:
    """Return a PathSpec matching gitignore content if present."""
    gitignore = root / ".gitignore"
    lines: List[str] = []
    if gitignore.is_file():
        with gitignore.open(encoding="utf-8") as gf:
            lines = gf.readlines()
    try:
        return PathSpec.from_lines("gitwildmatch", lines)
    except GitWildMatchPatternError as e:
        raise


def get_absolute_path(
    path: Path,
    root: Path,
) -> Path:
    return path if path.is_absolute() else root.joinpath(path)


def get_path_from_root(
    path: Path,
    root: Path,
) -> Optional[str]:
    """Get the path from root"""
    try:
        # abspath = path if path.is_absolute() else Path.cwd().joinpath(path)
        abspath = get_absolute_path(path=path, root=root)
        return abspath.resolve().relative_to(root).as_posix()
    except OSError as e:
        return None

    except ValueError:
        if path.is_symlink():
            return None

        raise


def gen_python_files(
    paths: Iterable[Path],
    root: Path,
    gitignore: Optional[PathSpec],
) -> Iterator[Path]:
    """Generate all files under `path` whose paths are not excluded by the
    `exclude_regex`, `extend_exclude`, or `force_exclude` regexes,
    but are included by the `include` regex.

    Symbolic links pointing outside of the `root` directory are ignored.

    """
    for child in paths:
        normalized_path = get_path_from_root(
            child,
            root,
        )
        if normalized_path is None:
            continue

        # First ignore files matching .gitignore, if passed
        if gitignore is not None and gitignore.match_file(normalized_path):
            continue

        normalized_path = "/" + normalized_path
        if child.is_dir():
            normalized_path += "/"

        if child.is_dir():
            # If gitignore is None, gitignore usage is disabled, while a Falsey
            # gitignore is when the directory doesn't have a .gitignore file.
            yield from gen_python_files(
                child.iterdir(),
                root,
                gitignore + get_gitignore(child) if gitignore is not None else None,
            )

        elif child.is_file():
            yield child


def get_files(
    paths: Iterable[str],
):
    root = find_project_root(())
    yield from gen_python_files(
        paths=(Path(src) for src in paths),
        root=root,
        gitignore=get_gitignore(root=root),
    )


# if __name__ == '__main__':
#     # print(find_project_root(None))
#
#     for x in gen_python_files([Path("/Users/aureliendidier/github.com/anteverse/pycaro/tests")], root=Path("/Users/aureliendidier/github.com/anteverse/pycaro"), gitignore=get_gitignore(Path("/Users/aureliendidier/github.com/anteverse/pycaro"))):
#         print(x)
#
#     m = ModuleChecker(module_name="tests.assets.case_simple_one_liner")
#
#     # print(get_gitignore(Path("/Users/aureliendidier/github.com/anteverse/pycaro")))
