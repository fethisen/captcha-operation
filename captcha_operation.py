import base64
import os
import time

import requests
from requests.structures import CaseInsensitiveDict
import json
import ast


class CaptchaOperation:
    """
    It is a class that consists of methods that automatically decode the images created for captcha
    usega call api: https://anti-captcha.com/apidoc/task-types/ImageToTextTask
    """

    CAPTCHA_IMAGE_NAME = "captcha.jpeg"
    CLIENT_KEY = "YOUR_API_KEY"

    def create_data_for_captcha_request(self, base64_text):
        task_dict = {}
        task_dict["type"] = "ImageToTextTask"
        task_dict["body"] = base64_text
        task_dict["case"] = "false"
        task_dict["phrase"] = "false"
        task_dict["numeric"] = "0"
        task_dict["math"] = "false"
        task_dict["minLength"] = "0"
        task_dict["maxLength"] = "0"

        dict = {}
        dict["clientKey"] = self.CLIENT_KEY
        dict["task"] = task_dict

        return json.dumps(dict)

    def get_task_result(self, task_id):
        url = "https://api.anti-captcha.com/getTaskResult"
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        dict = {}
        dict["clientKey"] = self.CLIENT_KEY
        dict["taskId"] = task_id
        resp = requests.post(url, headers=headers, data=json.dumps(dict))
        if resp.status_code == 200:
            dict_str = resp.content.decode("UTF-8")
            mydata = ast.literal_eval(dict_str)
            solution_dict = mydata["solution"]
            return solution_dict["text"]

    def get_text_of_captcha(self, image_base64):
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        url = "https://api.anti-captcha.com/createTask"

        resp = requests.post(url, headers=headers, data=self.create_data_for_captcha_request(image_base64))
        if resp.status_code == 200:
            dict_str = resp.content.decode("UTF-8")
            mydata = ast.literal_eval(dict_str)
            task_id = repr(mydata["taskId"])
            # https://anti-captcha.com/apidoc/task-types/ImageToTextTask
            # Use method getTaskResult to request the solution. Give the worker about 5 seconds before making your first request. If the worker is still busy, retry in 3 seconds.
            time.sleep(8)
            return self.get_task_result(task_id)

    def create_base64_from_image(self):
        with open(self.CAPTCHA_IMAGE_NAME, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())

        os.remove(self.CAPTCHA_IMAGE_NAME)
        return b64_string.decode('utf-8')

    def download_captcha_image(self, browser):
        with open(self.CAPTCHA_IMAGE_NAME, 'wb') as file:
            l = browser.find_element_by_xpath(
                '/html/body/form/div[3]/div[2]/table/tbody/tr[1]/td/div/table/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/img')
            file.write(l.screenshot_as_png)
