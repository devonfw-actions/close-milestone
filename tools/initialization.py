import getopt
import re
import sys

from tools.config import Config
from tools.github import GitHub
from tools.logger import log_info, log_error, log_warn


def init_non_git_config(config: Config):
    __process_params(config)

    ###################################################################################################################################

    if not hasattr(config, 'github_repo'):
        config.github_repo = ""
    repo_pattern = re.compile(r'[a-zA-Z]+/[a-zA-Z]+')
    while(not repo_pattern.match(config.github_repo)):
        if config.github_repo:
            log_error("'" + config.github_repo + "' is not a valid GitHub repository name.")
            sys.exit(1)

    log_info("Releasing against GitHub repository '"+config.github_repo+"'")
    config.git_repo_name = config.github_repo.split(sep='/')[1]
    config.git_repo_org = config.github_repo.split(sep='/')[0]


def init_git_dependent_config(config: Config, github: GitHub):

    if not hasattr(config, "release_version"):
        log_error("Release tag name not specified")
        sys.exit(1)
    else:
        log_info("Release tag name: {}".format(config.release_version))

    version_pattern_raw = r'(v?[0-9]+\.[0-9]+\.)([0-9]+)'
    version_pattern = re.compile(version_pattern_raw)
    if not hasattr(config, "next_version"):
        log_info("Next release name not specified.")
        if version_pattern.match(config.release_version):
            log_info("Increasing bugfix version by 1")
            for match in version_pattern.finditer(config.release_version):
                version_prefix = match.group(1)
                bugfix_version = match.group(2)
                bugfix_version_len = len(bugfix_version)
                new_bugfix_version = int(bugfix_version)+1
                new_bugfix_version_str = str(new_bugfix_version).zfill(bugfix_version_len)
                config.next_version = version_prefix + new_bugfix_version_str
                log_info("New version determined to be {}".format(config.next_version))
                break
        else:
            log_error("Could not determine version pattern. Supported version pattern is {}".format(version_pattern_raw))
            sys.exit(1)
    else:
        log_info("Next version: {}".format(config.next_version))

    config.tag_name = config.release_version
    config.expected_milestone_name = config.tag_name

    milestone = github.find_release_milestone()
    if milestone:
        log_info("Milestone '"+milestone.title+"' found!")
    else:
        log_error("Milestone not found! Searched for milestone with name '" + config.expected_milestone_name+"'.")
        sys.exit(1)


def __process_params(config: Config):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dg:hyv:t:", ["debug", "github-repo-id=", "help", "dry-run", "release-version", "github-token"])
    except getopt.GetoptError:
        __print_cmd_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-d", "--debug"):
            log_info("[ARGS] --debug: The script will require user interactions for each step.")
            config.debug = True
        elif opt in ("-g", "--github-repo-id"):
            log_info("[ARGS] GitHub repository to release against is set to " + arg)
            config.github_repo = arg
        elif opt in ("-h", "--help"):
            __print_cmd_help()
            sys.exit(0)
        elif opt in ("-y", "--dry-run"):
            config.dry_run = True
            log_info("[ARGS] --dry-run: No changes will be made on the Git repo.")
        elif opt in ("-v", "--release-version"):
            config.release_version = arg
            log_info("[ARGS] Release version to be released set to " + arg)
        elif opt in ("-t", "--github-token"):
            config.github_token = arg
            log_info("[ARGS] GitHub Token set")


def __print_cmd_help():
    log_info("""

Options:
  -d / --debug:           Script stops after each automatic step and asks the user to continue.
  -g / --github-repo-id   GitHub repository name to be released
  -h / --help:            Provides a short help about the intention and possible options.
  -y / --dry-run:         Will prevent from pushing to the remote repository, changing anything on GitHub
                          Issues/Milestones etc.
    """)
