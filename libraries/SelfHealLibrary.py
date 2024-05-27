from js_variables import js_get_element, js_get_elements
from llm_prompts import *
from openai import OpenAI
from rapidfuzz import fuzz
from pathlib import Path
from robot.api.deco import library, keyword
from robot.libraries.BuiltIn import BuiltIn
from robot.result import Keyword as KeywordResult
from robot.running import Keyword as KeywordData, LibraryKeyword 
from SeleniumLibrary import SeleniumLibrary
from tinydb import TinyDB, Query

import itertools
import json
import os
import datetime

@library(scope='TEST', listener='SELF')
class SelfHealLibrary:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.session: SeleniumLibrary = BuiltIn().get_library_instance("SeleniumLibrary")
        self.test_error_msg = ""
        self.testcase_name = ""
        self.failed_variable = ""
        self.answer = ""
        self.db = TinyDB(os.path.curdir + "/resources/locators/locators.json")
        self.candidate_level = BuiltIn().get_variable_value('${CANDIDATE_LEVEL}')
        self.candidates = ""

        self.file_to_be_fixed = ""
        self.line_to_be_fixed = ""
        self.file_backup = None
        self.retries = 0
        self.max_retries = 1

    @keyword
    def make_request_for_llm(self, model="openai/gpt-4-turbo"):
        """Makes request for LLM through open router ai API"""
        BuiltIn().log(f"Using: {model} language model.")
        self._get_candidates()
        messages = self._create_message_for_llm(self.test_error_msg, 
                                                self.testcase_name, 
                                                self.failed_variable, 
                                                self.candidates)
        self._log_llm_message(messages)
        answer = self._call_openai(model, messages)
        BuiltIn().log(f"Answer from LLM: {answer}")
        BuiltIn().log_to_console('\n' + answer)
        # next function used only for this thesis
        self._create_results_for_thesis(model, self.testcase_name, answer)
        self._find_and_replace_locator(answer)

    def _find_and_replace_locator(self, answer):
        new_locator = json.loads(answer)
        path = Path(os.getcwd())
        for f in path.rglob('*.robot'):
            if f.is_file():
                text = f.read_text()
                if self.failed_variable in text:
                    self._replace_text(f, new_locator['correct_locator'])
        for f in path.rglob('*.resource'):
            if f.is_file():
                text = f.read_text()
                if self.failed_variable in text:
                    self._replace_text(f, new_locator['correct_locator'])

    def _create_results_for_thesis(self, model, test_case, answer):
        now = datetime.datetime.now()
        date = datetime.datetime.strftime(now, '%d-%m-%Y')
        result_path = os.getcwd() + '/llm_results/'
        file_name = model + '_results_' + date + '.txt'
        if os.path.isfile(result_path + file_name):
            with open(result_path + file_name, 'a') as file:
                file.write('Test Case Name: ' + test_case + '\nModel used: ' + model + '\nModel answer:\n' + answer + '\n') 
        else:
            with open(result_path + file_name, 'w+') as file:
                file.write('Test Case Name: ' + test_case + '\nModel used: ' + model + '\nModel answer:\n' + answer + '\n')

    def _get_candidates(self):
        if self.candidate_level == "WEAK":
            self._get_candidates_weak()
        elif self.candidate_level == "STRONG":
            self._get_candidates_strong()

    def _log_llm_message(self, llm_message):
        BuiltIn().log(f"Request that will be sent to LLM: ")
        for message in llm_message:
            BuiltIn().log(message)    

    def _get_page_source(self):
        """Getting page source from currently open page at browser"""
        try:
            page_source = self.session.get_source()
            BuiltIn().log("Fetching page html source")
        except Exception as err:
            BuiltIn().log(f'Unexpected {err}, {type(err)}')
        
        return page_source

    def _get_all_page_elements(self):
        try:
            all_elements = self.session.execute_javascript(js_get_elements)
            BuiltIn().log("Fetched all elements from page")
        except Exception as err:
            BuiltIn().log(f'Unexpected {err}, {type(err)}')

        # turn all_elements into json
        
        return all_elements
    
#    @keyword
#    def try_to_fix(self):
#        self._replace_line(self.file_to_be_fixed, self.line_to_be_fixed-1, self.answer)
    
#    @keyword
#    def revert_changes(self):
#        self._revert_file_changes(self.file_to_be_fixed)

    def _create_message_for_llm(self, test_error_msg, testcase, variables, candidates=""):
        '''Creating request message for llm'''
        messages=[
            {"role": "system", "content": llm_role},    
        ]
        if test_error_msg:
            messages.append({"role": "user", "content": llm_test_error + str(test_error_msg).replace('"',"'")})
        if variables:
            messages.append({"role": "user", "content": llm_variables_used + variables})
        if testcase:
            messages.append({"role": "user", "content": llm_testcase + testcase})
        if candidates:
            messages.append({"role": "user", "content": llm_potential_candidates + candidates})  
        messages.append({"role": "user", "content": llm_answer})
        #BuiltIn.log(f"Request for LLM: {messages}")
        return messages

    def _call_openai(self, model, messages):
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="your_api_key"
        )

        completion = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return completion.choices[0].message.content

    def _start_test(self, data, result):
        self.testcase_name = result.name

    def _end_library_keyword(self, data: KeywordData, implementation: LibraryKeyword, result: KeywordResult):
        if not result.passed:
            if not self.failed_variable:
                self.failed_variable = self._parse_argument(result.args[0])
#                print(result.args[0])
            if not self.test_error_msg:
                self.test_error_msg = result.message
        else:
            library = implementation.owner
            if library.name == 'SeleniumLibrary':
                if result.args:
                    try:
                        self._save_locator_to_file(self._parse_argument(result.args[0]))
                    except Exception as err:
                        BuiltIn().log(f'Unexpected error when saving locator to DB: {err}, {type(err)}')
    
    def _save_locator_to_file(self, locator):
        locator = locator.replace('"',"'")
        webelem = self.session.get_webelement(locator)
        all_attributes = self.session.execute_javascript(js_get_element, 'ARGUMENTS', webelem)
        #print("ATTRIBUTES: " + str(all_attributes))
        BuiltIn().log(str(all_attributes))
        all_attributes_json = json.loads(all_attributes[1:-1])
        all_attributes_json['locator'] = locator
        Locators = Query()
        if self.db.search(Locators.locator == locator):
            BuiltIn().log("Locator already stored in local database")
        else:
            BuiltIn().log("Added following locator to database: "+ str(all_attributes_json))
            self.db.insert(all_attributes_json)
            
    def _parse_argument(self, argument):
        if "${" in argument:
            argument = BuiltIn().get_variable_value(argument)
        return argument
                
    def _get_candidates_weak(self, number_of_candidates=10):
        page_source = self._get_page_source()
        candidates = self._calc_closest_words(self.failed_variable, page_source)
        candidates = {k: v for k, v in sorted(candidates.items(), key=lambda item: item[1], reverse=True)}
        candidates = dict(itertools.islice(candidates.items(), number_of_candidates))
        for k, v in candidates.items():
            k = k.replace('"',"'")
            v = str("%.2f" % v)
            self.candidates = self.candidates + (f"{k}:{v}")

    def _get_candidates_strong(self, number_of_candidates=10):
        all_elements = self._get_all_page_elements()
        #BuiltIn().log(all_elements)
        all_elements_json = json.loads(all_elements)
        #print(str(all_elements_json))
        candidates = {}
        try:
            Locators = Query()
            locator = self.failed_variable
            target_element = self.db.search(Locators.locator == locator.replace('"',"'"))
            BuiltIn().log("Target element was found from database")
            BuiltIn().log(target_element)
        except:
            BuiltIn().log("Target element was not found from database, Self-healing not possible")

        if target_element:
            for element in all_elements_json:
                ratio = fuzz.ratio(str(target_element), str(element))
                data = {str(element) : ratio}
                candidates.update(data)
            candidates = {k: v for k, v in sorted(candidates.items(), key=lambda item: item[1], reverse=True)}
            candidates = dict(itertools.islice(candidates.items(), number_of_candidates))
            for k, v in candidates.items():
                k = k.replace('"',"'")
                v = str("%.2f" % v)
                self.candidates = self.candidates + (f"{k}:{v}")    

    def _calc_closest_words(self, locator, html):
        candidates = {}
        for line in str(html).splitlines():
            for word in line.split():
                ratio = fuzz.ratio(locator, word)
                data = {word : ratio}
                candidates.update(data)
        return candidates

    def _replace_text(self, file_name, new_locator):
        with open(file_name, 'r') as read_file:
            filedata = read_file.read()
            self.file_backup = read_file.read()
        filedata = filedata.replace(self.failed_variable, new_locator)
        with open(file_name, 'w') as write_file:
            write_file.write(filedata)

    def _revert_file_changes(self, file_name):
        file = open(file_name, 'w')
        file.writelines(self.file_backup)
        file.close()