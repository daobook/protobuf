'''generate Python API reference
'''

from pathlib import Path
from string import Template

INDEX_DOCS_DIR = Path(__file__).parent.resolve()
DOCS_DIR = INDEX_DOCS_DIR.parent.parent.parent/'python/google'
PYTHON_DIR = DOCS_DIR.parent
SOURCE_DIR = PYTHON_DIR / "google" / "protobuf"
SOURCE_POSIX = SOURCE_DIR.as_posix()

# Modules which are always included:
INCLUDED_MODULES = (
    "google.protobuf.internal.containers",
)

# Packages to ignore, including all modules (unless in INCLUDED_MODULES):
IGNORED_PACKAGES = (
    "compiler",
    "docs",
    "internal",
    "pyext",
    "util",
)

# Ignored module stems in all packages (unless in INCLUDED_MODULES):
IGNORED_MODULES = (
    "any_test_pb2",
    "api_pb2",
    "unittest",
    "source_context_pb2",
    "test_messages_proto3_pb2",
    "test_messages_proto2",
)

TOC_TEMPLATE = """% START REFTOC, generated by generate_docs.py.

```{toctree}
${toctree}
```
% END REFTOC.
"""

AUTOMODULE_TEMPLATE = """% DO NOT EDIT, generated by generate_docs.py.

${module}
${underline}


.. automodule:: ${module}
   :members:
   :inherited-members:
   :undoc-members:
"""


def find_modules():
    modules = []
    for module_path in SOURCE_DIR.glob("**/*.py"):
        # Determine the (dotted) relative package and module names.
        package_path = module_path.parent.relative_to(PYTHON_DIR)
        if package_path == SOURCE_DIR:
            package_name = ""
            module_name = module_path.stem
        else:
            package_name = package_path.as_posix().replace("/", ".")
            module_name = package_name + "." + module_path.stem

        # Filter: first, accept anything in the whitelist; then, reject anything
        # at package level, then module name level.
        if any(include == module_name for include in INCLUDED_MODULES):
            pass
        elif any(ignored in package_name for ignored in IGNORED_PACKAGES):
            continue
        elif any(ignored in module_path.stem for ignored in IGNORED_MODULES):
            continue

        if module_path.name == "__init__.py":
            modules.append(package_name)
        else:
            modules.append(module_name)
    modules.remove('google.protobuf')
    return modules


def write_automodule(module):
    t = Template(AUTOMODULE_TEMPLATE)
    contents = t.substitute(module=module, underline="=" * len(module))
    automodule_path = INDEX_DOCS_DIR.joinpath(
        *module.split(".")).with_suffix(".rst")
    try:
        automodule_path.parent.mkdir(parents=True)
    except FileExistsError:
        pass
    with open(automodule_path, "w") as automodule_file:
        automodule_file.write(contents)


def replace_toc(modules):
    toctree = [module.replace(".", "/") for module in modules]
    toctree = "\n".join(toctree)
    t = Template(TOC_TEMPLATE)
    toc = t.substitute(toctree=toctree)
    with open(INDEX_DOCS_DIR / "index_toc.txt", "w") as index_file:
        index_file.write(toc)


def main():
    modules = list(sorted(find_modules()))
    for module in modules:
        print("Generating reference for {}".format(module))
        write_automodule(module)
    print("Generating index_toc.txt")
    replace_toc(modules)


if __name__ == "__main__":
    main()
