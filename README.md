# git-puller

## Description
*git-puller* is a small python script that will loop in all the git repositories in a parent folder,
checkout the branch provided as a parameter and pull changes from origin.

## Installation
Clone the repository
```bash
git clone https://github.com/ldalamagas/git-puller.git

```
Install using the setup.py
```bash
cd git-puller
python setup.py install
```
## Usage
Get help
```bash
git-puller -h
usage: git-puller [-h] [--branch BRANCH] parent-directory

Git Puller

positional arguments:
  parent-directory      Parent directory hosting git repositories

optional arguments:
  -h, --help            show this help message and exit
  --branch BRANCH, -b BRANCH
                        The branch to update
```
Example
```bash
git-puller /some/folder/containing/git/repositories/ --branch master
```
**Note:** if no branch is provided, **develop** branch will be picked as default