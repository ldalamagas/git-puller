from setuptools import setup, find_packages

setup(
    name="git-puller",
    version="0.0.1",
    packages=find_packages("src"),
    package_dir={'': 'src'},
    url="",
    license="",
    author="lefteris",
    author_email="",
    description="",
    entry_points={
        "console_scripts": [
            "git-puller=gitpuller.shell:main",
        ]},
    install_requires=["GitPython"]
)
