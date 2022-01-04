class Config():

    def __init__(self):
        self.root_path: str
        self.temp_root_path: str

        self.dry_run: bool = False
        self.debug: bool = False

        self.github_token: str

        self.github_repo: str
        self.git_repo_name: str
        self.git_repo_org: str

        self.tag_name: str

        self.release_version: str
        self.next_version: str

        self.expected_milestone_name: str

    def github_closed_milestone_url(self, milestone_number: int):
        return "https://github.com/" + self.github_repo + "/milestone/" + str(milestone_number)+"?closed=1"
