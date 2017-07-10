#!/bin/bash

set -e

# TODO(mcsalgado): better check for this thing to actually be a path and maybe even
# a git repository.
if [[ -z "$1" ]]; then
    echo "You must specify a repository path"
    exit 1
fi

repo_dir="$1"

git_version="$(git --version | awk '{ print $3 }')"
minimum_git_version="1.8.3.2"
if [[ "$git_version" = "$(echo -e "$git_version\n$minimum_git_version" | sort -V | head -n1)" ]]; then
    echo "Your git version is too old ($git_version < $minimum_git_version) and will mess up with these hooks"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "You don't have python3 installed."
    echo "Please install it using yum or apt-get or something."
    exit 1
fi

if ! python3 -c "import tkinter" &> /dev/null; then
    echo "You don't have tkinter installed in your system."
    echo "You should install it if you plan to use git with a gui instead of the command line."
    echo "Tip: if you're on Ubuntu the command is ´sudo apt-get install python3-tk´"
fi

pushd "$(dirname $0)"
hooks_repo_toplevel="$(git rev-parse --show-toplevel)"
popd

pushd "$repo_dir"
actual_repo_toplevel="$(git rev-parse --show-toplevel)"
popd

pushd "$actual_repo_toplevel"
git config alias.tst '!.git/hooks/post-commit'
popd

ln -sf "$hooks_repo_toplevel"/post-commit "$actual_repo_toplevel"/.git/hooks/post-commit
chmod u+x "$actual_repo_toplevel"/.git/hooks/post-commit

ln -sf "$hooks_repo_toplevel"/pre-push "$actual_repo_toplevel"/.git/hooks/pre-push
chmod u+x "$actual_repo_toplevel"/.git/hooks/pre-push

ln -sf "$hooks_repo_toplevel"/git_time_spent_tracking.py "$actual_repo_toplevel"/.git/hooks/git_time_spent_tracking.py
chmod u+x "$actual_repo_toplevel"/.git/hooks/git_time_spent_tracking.py

echo "The hooks were linked to $repo_dir successfully!"
