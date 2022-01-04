import sys
import logging

from pprint import pprint
from github.Milestone import Milestone

sys.path.append(".")

from tools.config import Config
from tools.github import GitHub
from tools.validation import check_running_in_bash
from tools.user_interface import prompt_yesno_question
from tools.initialization import init_non_git_config, init_git_dependent_config
from tools.logger import log_step, log_debug, log_info, log_info_dry, log_warn

# This log level is a global log level of the logging framework.
# Has to be set within the script as it starts logging everything also from used frameworks
# which is too much for testing purposes only
logging.getLogger('').setLevel(logging.INFO)

#####################################################################

def __log_step(message: str):
    log_step(message)

    global git_repo
    global config
    if config.debug and not prompt_yesno_question("[DEBUG] Continue with next step '"+message+"'?"):
        sys.exit()

#####################################################################
    
#############################
log_step("Initialization...")
#############################

check_running_in_bash()

config = Config()
init_non_git_config(config)

github = GitHub(config)
init_git_dependent_config(config, github)

if(config.debug):
    log_debug("Current config:")
    pprint(vars(config))
    if not prompt_yesno_question("[DEBUG] Continue?"):
        sys.exit()

report_messages = []

#####################################################################

#############################
__log_step("Close GitHub Milestone...")
#############################
milestone: Milestone = github.find_release_milestone()
if config.dry_run:
    log_info_dry("Would close the milestone: " + milestone.title)
else:
    if (milestone.state == "closed"):
        log_warn("Milestone '"+milestone.title + "' was already closed, please check.")
    else:
        if milestone.description is None:
            milestone.edit(milestone.title, "closed", "Void description error")
        else:
            milestone.edit(milestone.title, "closed", milestone.description)
        log_info("New status of Milestone '" + milestone.title + "' is: " + milestone.state)

#############################
__log_step("Create new GitHub release...")
#############################
github.create_release(milestone)

#############################
__log_step("Create new GitHub milestone...")
#############################
if config.dry_run:
    log_info_dry("Would create a new milestone")
else:
    if not github.create_next_release_milestone():
        log_warn("Failed to create the next release milestone (is it already created?).")

