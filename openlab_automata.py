import json
import re

import requests
from xeger import Xeger


class OpenLabAutomata:
    def __init__(self, host):
        self.LOGIN_URL = 'http://%s/site/login' % host
        self.EXERCISE_INDEX_URL = 'http://%s/studentExercise/index' % host
        self.EXERCISE_GET_NODE_URL = 'http://%s/studentExercise/ajaxGetNodes' % host
        self.EXERCISE_SUBMIT_SELECT_URL = 'http://%s/studentExercise/ajaxSubmitSelect' % host
        self.EXERCISE_SUBMIT_FILL_URL = 'http://%s/studentExercise/ajaxSubmitFill' % host

        self._session = requests.session()
        self.user = None  # type: dict
        self.classes = None  # type: list

    def login(self, username, password):
        try:
            form = {
                'LoginForm[email]': username,
                'LoginForm[password]': password
            }
            resp = self._session.post(self.LOGIN_URL, form)
            resp_str = resp.content.decode()

            reg = re.compile('姓名:([^<]*)</div>')
            [nickname] = reg.findall(resp_str)

            self.user = {
                'username': username,
                'password': password,
                'nickname': nickname,
            }

            reg = re.compile(
                '<td><a href="/studentClass/index\?currentClassId=(\d*)">(.*?)</a></td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>')
            classes_str = reg.findall(resp_str)
            self.classes = [{'id': i[0], 'time': i[1], 'name': i[2], 'teacher': i[3], 'score': i[3]} for i in
                            classes_str]

            return True
        except:
            return False

    def get_exercise_root_nodes(self, class_id):
        try:
            form = {
                'currentClassId': class_id,
            }
            resp = self._session.get(self.EXERCISE_INDEX_URL, params=form)
            resp_str = resp.content.decode()
            reg = re.compile('nodes = (\[.*\])')
            [json_str] = reg.findall(resp_str)
            data = json.loads(json_str)
            return data
        except:
            return None

    def get_exercise_nodes(self, node_id, node_type, real_id):
        try:
            form = {
                'id': node_id,
                'count': 100,
                'type': node_type,
                'realId': real_id,
                'ztreeTotal': 1,
            }
            resp = self._session.get(self.EXERCISE_GET_NODE_URL, params=form)
            resp_str = resp.content.decode()
            data = json.loads(resp_str)
            return data
        except:
            return None

    def get_exercise_nodes_all(self, root_node):
        result = []
        nodes = self.get_exercise_nodes(root_node['id'], root_node['type'], root_node['realId'])
        for node in nodes:
            result.append(node)
            if node['type'] != 'exercise':
                result += self.get_exercise_nodes_all(node)
        return result

    def submit_select(self, p_id, real_id, score, class_id, answer_num: list):
        try:
            ids_data = answer_num.copy()
            if 0 in ids_data:
                ids_data.remove(0)
            ids_str = ','.join(ids_data)

            form = {
                'exerciseId': real_id,
                'ids': ids_str,
                'score': score,
                'currentClassId': class_id,
                'section_id': p_id,
            }
            resp = self._session.get(self.EXERCISE_SUBMIT_SELECT_URL, params=form)
            resp_str = resp.content.decode()
            data = json.loads(resp_str)
            return bool(data['correct_sign'])
        except:
            return None

    def submit_fill(self, p_id, real_id, score, class_id, content=None):
        try:
            form_get = {
                'currentClassId': class_id,
            }
            form = {
                'exerciseId': real_id,
                'text': content,
                'score': score,
                'my_xrcs_exam_id': 0,
                'section_id': p_id,
            }
            resp = self._session.post(self.EXERCISE_SUBMIT_FILL_URL, data=form, params=form_get)
            resp_str = resp.content.decode()
            data = json.loads(resp_str)
            if content is None:
                print(data)
                answer = self._generate_answer(data['test_txt'])
                return self.submit_fill(p_id, real_id, score, class_id, answer)
            return bool(data['correct_sign'])
        except:
            return None

    def _generate_answer(self, test_txt):
        reg = re.compile('0\((.*?)\);')
        regs_str = [i for i in reg.findall(test_txt)]

        result = ''
        x = Xeger(limit=1)
        x._alphabets['whitespace'] = ' '
        x._cases['any'] = lambda x: '.'
        for reg_str in regs_str:
            if result != '':
                result += '\n'
            result += x.xeger(reg_str).strip()

        return result
