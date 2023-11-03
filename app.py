import os
os.system("pip install pyautogen")
os.system("pip install streamlit")

import autogen
import streamlit_app

key1 = streamlit_app.openaikey
config_list = [
    {
        'model': 'gpt-4',
        'api_key': key1
    }
]

llm_config={
    "request_timeout": 600,
    "seed": 42,
    "config_list": config_list,
    "retry_wait_time": 30,
    "temperature": 0
}

assistant = autogen.AssistantAgent(
    name="Python Programmer",
    llm_config=llm_config,
    system_message="""You are a python programmer. While writing code, do not write any comments. You just have to write only necessary code, no comments."""
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=30,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "hackathon", "use_docker":False},
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet. You have to execute the codes provided by assistant and generate the desired files in the working directory."""
)
with open("target_variable.txt", "r") as f:
    target_variable = f.read()

with open("eval_metric.txt", "r") as f:
    eval_metric = f.read()   

with open("eval_desc.txt", "r") as f:
    eval_desc = f.read()

with open("rules.txt", "r") as f:
    rules = f.read()

task = """
Your task is to {rules} where you need to predict {target_variable}.
The relevant datasets (train.csv and test.csv) are available in the working directory.
To install a library, use sh command with pip, do not use '!' before 'pip install'.
The criteria for performance is optimizing the {eval_metric} which is {eval_desc}.
Perform the necessary data imputation and  do not drop target variable while preparing the train data. 
You can create new features which can help improve {eval_metric} in addition to the existing features.
Try out different baseline models for algorithms like gradient boostong, random forest, xgboost, catboost etc and output their validation scores in a separate .txt file. Remember to specify verbose as -1 or False to prevent showing model logs.
Select the model with highest accuracy and tune hyperparameters for it using grid search and use the final best model for predictions on test dataset.
Create a submission file submission.csv in the working directory and while generating use the IDs in test.csv present in working directory. 
Once the code is finalised and the submission file is created, create a file named 'code.py' in the working directory which will contain the entire final code from scratch till creating the submission file.
 
Do not terminate until both these files have been successfully created. 
""".format(rules=rules, target_variable=target_variable, eval_metric=eval_metric, eval_desc=eval_desc)
user_proxy.initiate_chat(
    assistant,
    message=task
)
