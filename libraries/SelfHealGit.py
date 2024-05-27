from git import Repo
from robot.api.deco import library, keyword

@library(scope='TEST')
class SelfHealGit:

    def __init__(self):
        self.repo = Repo(search_parent_directories=True)
        self.original_branch = self.repo.active_branch
        self.branch = None
    
    @keyword
    def commit_to_different_branch(self, branch_name='self-heal', message='Commit from selfheal library'):        
        self.branch = [b for b in self.repo.branches if b.name == branch_name]

        if len(self.branch) == 0:
            self.branch = self.repo.create_head(branch_name)
        else:
            self.branch = self.branch[0]
        self._switch_branch()
#        self._add_and_commit(message)
        self._checkout_original_branch()
        
    def _switch_branch(self):
        self.branch.checkout()

    def _add_and_commit(self, message):
        self.repo.git.add('*')
        self.repo.git.commit(message)

    def _push_branch(self, branch):
        self.repo.git.push('--set-upstream', 'origin', branch)

    def _checkout_original_branch(self):
        self.original_branch.checkout()