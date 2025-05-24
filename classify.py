from processor_regex import classify_with_regex
from processor_bert import classify_with_bert
from processor_llm import classify_with_llm
from emailer import send_workflow_error_email_batch

def classify(logs, recipient_email=None):
    enriched_labels = []
    workflow_errors = []

    for source, log_msg in logs:
        label_info = classify_log(source, log_msg)
        enriched_labels.append(label_info)

        if label_info["target_label"] == "Workflow Error":
            workflow_errors.append({"source": source, "log_message": log_msg})
    
    # Send email if applicable
    if recipient_email and workflow_errors:
        import pandas as pd
        error_df = pd.DataFrame(workflow_errors)
        send_workflow_error_email_batch(error_df, recipient_email)

    return enriched_labels

def classify_log(source, log_message):
    # LegacyCRM uses LLM
    if source == "LegacyCRM":
        label, confidence = classify_with_llm(log_message)
        method = "LLM"
    else:
        label = classify_with_regex(log_message)
        if label is not None:
            confidence = 1.0
            method = "Regex"
        else:
            label, confidence = classify_with_bert(log_message)
            method = "Transformer"

    return {
        "target_label": label,
        "used_method": method,
        "confidence": confidence
    }

def classify_csv(input_file, recipient_email=None):
    import pandas as pd
    df = pd.read_csv(input_file)
    results = classify(list(zip(df["source"], df["log_message"])), recipient_email=recipient_email)

    df["target_label"] = [r["target_label"] for r in results]
    df["used_method"] = [r["used_method"] for r in results]
    df["confidence"] = [r["confidence"] for r in results]

    output_file = "resources/output.csv"
    df.to_csv(output_file, index=False)  


if __name__ == '__main__':
    classify_csv("resources/test.csv", recipient_email="example@gmail.com")
    # logs = [
    #     ("ModernCRM", "IP 192.168.133.114 blocked due to potential attack"),
    #     ("BillingSystem", "User User12345 logged in."),
    #     ("AnalyticsEngine", "File data_6957.csv uploaded successfully by user User265."),
    #     ("AnalyticsEngine", "Backup completed successfully."),
    #     ("ModernHR", "GET /v2/54fadb412c4e40cdbaed9335e4c35a9e/servers/detail HTTP/1.1 RCODE  200 len: 1583 time: 0.1878400"),
    #     ("ModernHR", "Admin access escalation detected for user 9429"),
    #     ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."),
    #     ("LegacyCRM", "Invoice generation process aborted for order ID 8910 due to invalid tax calculation module."),
    #     ("LegacyCRM", "The 'BulkEmailSender' feature is no longer supported. Use 'EmailCampaignManager' for improved functionality."),
    #     ("LegacyCRM", " The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025")
    # ]

    # classified_logs = classify(logs)
    # print(classified_logs)