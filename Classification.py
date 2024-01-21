import datetime
import io
from dataclasses import dataclass

@dataclass
class Classification:


    def __init__(self, classification_id: int, user_name: str, user_id: str, user_ip: str,
                 workflow_id: str, workflow_name: str, workflow_version: str, started_at: datetime.datetime, gold_standard: str, expert: str, subject_id: int):
        self._classification_id = classification_id
        self._user_name = user_name
        self._user_id = user_id
        self._user_ip = user_ip
        self._workflow_id = workflow_id
        self._workflow_name = workflow_name
        self._workflow_version = workflow_version
        self._started_at = started_at
        self._gold_standard = gold_standard
        self._expert = expert
        self._subject_id = subject_id

    @property
    def classification_id(self):
        return self._classification_id

    @classification_id.setter
    def classification_id(self, new_classification_id):
        self._classification_id = new_classification_id

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, new_user_name):
        self._user_name = new_user_name

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, new_user_id):
        self._user_id = new_user_id

    @property
    def user_ip(self):
        return self._user_ip

    @user_ip.setter
    def user_ip(self, new_user_ip):
        self._user_ip = new_user_ip


    @property
    def workflow_id(self):
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, new_workflow_id):
        self._workflow_id = new_workflow_id

    @property
    def workflow_name(self):
        return self._workflow_name

    @workflow_name.setter
    def workflow_name(self, new_workflow_name):
        self._workflow_name = new_workflow_name

    @property
    def workflow_version(self):
        return self._workflow_version

    @workflow_version.setter
    def workflow_version(self, new_workflow_version):
        self._workflow_version = new_workflow_version

    @property
    def started_at(self):
        return self._started_at

    @started_at.setter
    def started_at(self, new_started_at):
        self._started_at = new_started_at

    @property
    def gold_standard(self):
        return self._gold_standard

    @gold_standard.setter
    def gold_standard(self, new_gold_standard):
        self._gold_standard = new_gold_standard

    @property
    def expert(self):
        return self._expert

    @expert.setter
    def expert(self, new_expert):
        self._expert = new_expert

    @property
    def subject_id(self):
        return self._subject_id

    @subject_id.setter
    def subject_id(self, new_subject_id):
        self._subject_id = new_subject_id
