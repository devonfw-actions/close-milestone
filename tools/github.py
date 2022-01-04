import os
import sys

from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset
from github.GithubException import UnknownObjectException, GithubException, BadCredentialsException
from github.Issue import Issue
from github.MainClass import Github
from github.Milestone import Milestone
from github.PaginatedList import PaginatedList
from github.Repository import Repository

from tools.config import Config
from tools.github_cache import GitHubCache
from tools.logger import log_error, log_info, log_info_dry, log_debug

class GitHub:

    def __init__(self, config: Config) -> None:
        self.__config: Config = config

        self.__authenticate_git_user()
        self.__initialize_repository_object()

    def __initialize_repository_object(self):
        self.__cache = GitHubCache()
        try:
            org = self.__github.get_organization(self.__config.git_repo_org)
            if self.__config.debug:
                log_debug("Organization found.")
        except UnknownObjectException as e:
            if self.__config.debug:
                log_debug("Organization not found. Try interpreting " + self.__config.git_repo_org + " as user...")
            org = self.__github.get_user(self.__config.git_repo_org)
            if self.__config.debug:
                log_debug("User found.")
            print(str(e))

        self.__repo: Repository = org.get_repo(self.__config.git_repo_name)

    # This script is responsible for the authentication of git user
    def __authenticate_git_user(self):
        try:
            self.__github = Github(self.__config.github_token)
            log_info("Authenticated.")
        except BadCredentialsException as e:
            log_info("Authentication error, please try again.")
            print(str(e))

    def find_issue(self, issue_number: int) -> Issue:
        '''Search for the Release issue to be used, if not found, exit'''
        # caching!
        if issue_number in self.__cache.issues:
            log_info("Issue with number " + str(issue_number) + " found.")
            return self.__cache.issues[issue_number]
        else:
            log_debug("Issue not found in cache, retrieving from GitHub...")

        try:
            self.__cache.issues.update({issue_number: self.__repo.get_issue(issue_number)})
            log_info("Issue with number " + str(issue_number) + " found.")
            return self.__cache.issues[issue_number]
        except UnknownObjectException:
            return None

    def __request_milestone_list(self) -> PaginatedList:
        # caching!
        try:
            return self.__cache.milestones
        except AttributeError:
            log_debug("Milestones not found in cache, retrieving from GitHub...")

        try:
            milestones: PaginatedList = self.__repo.get_milestones(state="all")
            self.__cache.milestones = milestones
            return milestones
        except GithubException as e:
            log_error('Could not retrieve milestones')
            print(str(e))
            sys.exit(1)

    def find_release_milestone(self) -> Milestone:
        milestones: PaginatedList = self.__request_milestone_list()

        for milestone in milestones:
            milestone_title_in_git = milestone.title
            if self.__config.expected_milestone_name in milestone_title_in_git:
                return milestone
        return None

    def create_next_release_milestone(self) -> Milestone:
        new_mile_title = self.__config.expected_milestone_name.replace(self.__config.release_version,
                                                                       self.__config.next_version)
        if self.__config.dry_run:
            log_info_dry("Would now create a new milestone with title '" + new_mile_title + "'.")
            return None

        log_info("Creating milestone '" + new_mile_title + "' for next release...")
        try:
            milestone: Milestone = self.__repo.create_milestone(title=new_mile_title, state="open")
            log_info("New milestone created!")
            return milestone
        except GithubException as e:
            log_info("Could not create milestone!")
            print(str(e))
            return None

    def create_release(self, closed_milestone: Milestone) -> GitRelease:
        if self.__config.dry_run:
            log_info_dry("Would create a new GitHub release")
            return None

        url_milestone = self.__config.github_closed_milestone_url(closed_milestone.number)
        release_title = self.__config.release_version
        release_text = "[ChangeLog by Milestone](" + url_milestone + ")"
        
        try:
            release: GitRelease = self.__repo.create_git_release(self.__config.tag_name, release_title,
                                                                 release_text, draft=False, prerelease=False) 
            #,generate_release_notes=True => generate release notes possible after PR merge PyGithub/PyGithub#2137
            #new_release_body = release.body + "\n\n" + release_text
            #release.update_release(body=new_release_body)
            return release
        except GithubException as e:
            log_error("Could not create release.")
            print(str(e))
            sys.exit(1)
