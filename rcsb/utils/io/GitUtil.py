##
# File: GitUtil.py
# Date: 17-Jul-2021
#
# Simple git utilities to perform status, clone, add, push and pull operations.
#
# Updates:
#
##

__docformat__ = "google en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Apache 2.0"

# pylint: disable=assigning-non-slot
#
import logging

from git import Repo

logger = logging.getLogger(__name__)


class GitUtil(object):
    """Simple git utilities to perform status, clone, add, push and pull operations."""

    def __init__(self, token=None, repositoryHost="github.com"):
        """Set GitHub personal access token and repository host.

        Args:
            token (str,optional): GitHub personal access token. Defaults to None.
            repositoryHost (str, optional): repository host name.  Defaults to github.com.
        """
        self.__token = token
        self.__repositoryHost = repositoryHost

    def clone(self, repositoryPath, localRepositoryPath, branch="master"):
        """Clone a GitHub repository to a local repository path.

        Args:
            repositoryPath (str): GitHub repository path (rcsb/py-mmcif)
            localRepositoryPath (str): local repository directory path

        Returns:
            (bool):  True for success or False otherwise
        """
        try:
            remote = f"https://{self.__token}@{self.__repositoryHost}/{repositoryPath}" if self.__token else f"https://{self.__repositoryHost}/{repositoryPath}"
            Repo.clone_from(remote, localRepositoryPath, branch=branch)
        except Exception as e:
            logger.exception("Failing for %r %r (%r) with %s", repositoryPath, localRepositoryPath, branch, str(e))
        return True

    def status(self, localRepositoryPath, branch="master"):
        """Get repository status.

        Args:
            localRepositoryPath (str): local repository directory path

        Returns:
            str: status message
        """
        repo = Repo(localRepositoryPath)
        return repo.git.status(branch)

    def addAll(self, localRepositoryPath, branch="master", remote="origin"):
        """Add/stage any unstaged artifact(s) to the repository (git add -a).

        Args:
            localRepositoryPath (str): local repository directory path
            branch (str, optional): branch name. Defaults to "master".
            remote (str, optional): remote name. Defaults to "origin".

        Returns:
            bool: True for success or False otherwise
        """
        try:
            repo = Repo(localRepositoryPath)
            remoteBranches = list(repo.branches)
            if branch not in remoteBranches:
                origin = repo.remote(name=remote)
                repo.head.reference = repo.create_head(branch)
                repo.head.reference.set_tracking_branch(origin.refs.master)
            repo.git.checkout(branch)
            logger.info("Active branch: %s", repo.active_branch)
            # repo.git.add(update=True)
            repo.git.add(all=True)
            stagedFiles = repo.index.diff("HEAD")
            logger.info("Staged files: %r", [sf.a_path for sf in stagedFiles])
            ok = len(stagedFiles) > 0
            if repo.untracked_files:
                logger.info("Untracked files: %r", repo.untracked_files)
                ok = False
            return ok
        except Exception as e:
            logger.exception("Failing for %r (%r) with %s", localRepositoryPath, branch, str(e))
        return False

    def commit(self, localRepositoryPath, commitMessage="GitUtil automated update", branch="master"):
        """Commit staged changes to the repository.

        Args:
            localRepositoryPath (str): local repository directory path
            commitMessage (str, optional): commit message. Defaults to "GitUtil automated update".
            branch (str, optional): branch name. Defaults to "master".

        Returns:
            bool: True for success or False otherwise
        """
        try:
            repo = Repo(localRepositoryPath)
            repo.git.checkout(branch)
            logger.info("Branch %s", repo.active_branch)
            commitRet = repo.index.commit(commitMessage)
            logger.debug("Commit status %r", commitRet)
            return True
        except Exception as e:
            logger.exception("Failing commit for %r (%r) with %s", localRepositoryPath, branch, str(e))
        return False

    def push(self, localRepositoryPath, remote="origin", branch="master"):
        """Push staged changes to the remote repository service.

        Args:
            localRepositoryPath (str): local repository directory path
            remote (str, optional): remote name. Defaults to "origin".
            branch (str, optional): branch name. Defaults to "master".

        Returns:
             bool: True for success or False otherwise
        """
        #
        try:
            repo = Repo(localRepositoryPath)
            origin = repo.remote(name=remote)
            pushRet = origin.push(branch)[0]
            logger.debug("Push returns %s", pushRet.summary.strip())
            return True
        except Exception as e:
            logger.exception("Failing push for %r (%r) with %s", localRepositoryPath, branch, str(e))
        return False

    def pull(self, localRepositoryPath, remote="origin", branch="master"):
        """Pull changes from the remote repository to the local working copy.

        Args:
            localRepositoryPath (str): local repository directory path
            remote (str, optional): remote name. Defaults to "origin".
            branch (str, optional): branch name. Defaults to "master".

        Returns:
             bool: True for success or False otherwise
        """
        #
        try:
            repo = Repo(localRepositoryPath)
            origin = repo.remote(name=remote)
            fInfo = origin.pull(branch)[0]
            fS = fInfo.note.strip()
            if fS:
                logger.info("Pull returns %s", fInfo.note.strip())
            return True
        except Exception as e:
            logger.exception("Failing push for %r (%r) with %s", localRepositoryPath, branch, str(e))
        return False
