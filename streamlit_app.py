import streamlit as st
import os
import pandas as pd
import subprocess
import time

def main():
    
    st.title("Data Science Agent")
    # Sidebar
    st.sidebar.header("Configuration")
    openaikey = st.sidebar.text_input("Provide OpenAI Key", "yourkey")
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
        process = subprocess.Popen(["python", "app.py"])
        process.wait()
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

if __name__ == "__main__":
    main()
