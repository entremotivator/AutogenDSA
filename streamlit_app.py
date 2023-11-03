import os
import streamlit as st
import pandas as pd
import subprocess
import autogen
import time


st.title("Data Science Agent")
    # Sidebar
st.sidebar.header("Configuration")
openaikey = st.sidebar.text_input("OpenAI Key", "Type your Key")
target_variable = st.sidebar.text_input("Target Variable", "target")
eval_metrics = ["MAE", "MSE", "RMSE", "R-squared", "Accuracy", "F1 Score"]
selected_metric = st.sidebar.selectbox("Select Evaluation Metric", eval_metrics)

    # Conditional mapping for evaluation metric descriptions
if selected_metric == "MAE":
    eval_metric_desc = "the average absolute errors between predicted and actual values."
elif selected_metric == "MSE":
    eval_metric_desc = "the average squared errors between predicted and actual values."
elif selected_metric == "RMSE":
    eval_metric_desc = "the square root of the Mean Squared Error."
elif selected_metric == "R-squared":
    eval_metric_desc = "the proportion of the variance in the dependent variable explained by the independent variables."
elif selected_metric == "Accuracy":
    eval_metric_desc = "the percentage of correctly predicted values in a classification task."
elif selected_metric == "F1 Score":
    eval_metric_desc = "the harmonic mean of precision and recall, providing a balance between precision and recall."

rules = st.sidebar.text_input("Rules for task", "as specified on kaggle")

    # File Upload
st.header("Upload Train and Test Files")
train_file = st.file_uploader("Upload Train File", type=["csv", "xlsx"])
test_file = st.file_uploader("Upload Test File", type=["csv", "xlsx"])

if st.button("Upload Files"):
    if train_file is not None and test_file is not None:
        train_filename = os.path.join("hackathon", "train.csv")
        test_filename = os.path.join("hackathon", "test.csv")
        os.makedirs("hackathon", exist_ok=True)
        with open(train_filename, "wb") as train_f, open(test_filename, "wb") as test_f:
            train_f.write(train_file.read())
            test_f.write(test_file.read())

            # Store the target variable and eval_metric in text files
        with open("target_variable.txt", "w") as f:
            f.write(target_variable)
        with open("eval_metric.txt", "w") as f:
            f.write(selected_metric)
        with open("eval_desc.txt", "w") as f:
            f.write(eval_metric_desc)
        with open("rules.txt", "w") as f:
            f.write(rules)    


        st.success("Files uploaded and configuration saved.")
    else:
        st.warning("Please upload both train and test files.")

    # "Run" button
if st.button("Run"):
        # Run the Python script using subprocess
    config_list = [
    {
        'model': 'gpt-4',
        'api_key': openaikey
    }
    ]

    llm_config={
        "request_timeout": 600,
    "seed": 69,
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
    To install a library, use sh command with pip, do not use '!' before 'pip install'. Always remember to import all necessary libraries during each code execution
    The criteria for performance is optimizing the {eval_metric} which is {eval_desc}.
    Perform the necessary data imputation and  do not drop target variable while preparing the train data. 
    You can create new features which can help improve {eval_metric} in addition to the existing features.
    Try out different baseline models for algorithms like gradient boosting, random forest, xgboost etc and output their validation scores in a separate .txt file. Remember to specify verbose as -1 or False to prevent showing model logs.
    Select the model with highest accuracy and tune hyperparameters for it using grid search and use the final best model for predictions on test dataset.
    Create a submission file submission.csv in the working directory and while generating use the IDs in test.csv present in working directory. 
    Once the code is finalised and the submission file is created, create a file named 'code.py' in the working directory which will contain the entire final code from scratch till creating the submission file.
    
    Do not terminate until both these files have been successfully created. 
    """.format(rules=rules, target_variable=target_variable, eval_metric=eval_metric, eval_desc=eval_desc)
    user_proxy.initiate_chat(
        assistant,
        message=task
    )
        
    # process = subprocess.Popen(["python", "app.py"])
    # process.wait()
    st.success("Python script executed successfully.")

        #st.success("Submission.csv has been generated.")

    # Provide a download link for the generated submission.csv
if os.path.exists("hackathon/submission.csv"):
    download_button = st.download_button(
        label="Download Results",
        data=open("hackathon/submission.csv", "rb").read(),
        key="download_submission_file",
        file_name="submission.csv",
    )
if os.path.exists("hackathon/code.py"):
    download_button = st.download_button(
        label="Download Code",
        data=open("hackathon/code.py", "rb").read(),
        key="download_code",
        file_name="code.py",
    )    

   
