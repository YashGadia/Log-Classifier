import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import io

# --- Streamlit Page Config ---
st.set_page_config(page_title="Log Classifier", layout="wide")

st.title("🔍 Log Classification Tool")
st.markdown("Upload a CSV file with **`source`** and **`log_message`** columns to classify logs.")

# --- Upload Section ---
uploaded_file = st.file_uploader("📤 Choose a CSV file", type="csv")

# --- Email Input ---
email = st.text_input("📧 Enter your email to receive Error alerts", placeholder="example@gmail.com")

if uploaded_file:
    try:
        # Read and preview the CSV
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Uploaded File Preview")
        st.dataframe(df.head())

        # Check for required columns
        if 'source' not in df.columns or 'log_message' not in df.columns:
            st.error("❌ CSV must contain 'source' and 'log_message' columns.")
        else:
            # Submit to FastAPI for classification
            if st.button("🚀 Classify Logs"):
                with st.spinner("🔄 Classifying logs..."):
                    files = {"file": ("logs.csv", uploaded_file.getvalue(), "text/csv")}
                    params = {"email": email} if email else {}

                    response = requests.post("http://localhost:8000/classify/", files=files, params=params)

                if response.status_code == 200:
                    # Load classified CSV
                    result_df = pd.read_csv(io.BytesIO(response.content))
                    st.success("✅ Logs classified successfully!")

                    # Show result preview
                    st.subheader("📄 Classified Results")
                    st.dataframe(result_df.head())

                    # --- Visualizations ---
                    st.subheader("📊 Visual Analytics")

                    # 1. Label Distribution
                    if "target_label" in result_df.columns:
                        fig1 = px.histogram(result_df, x="target_label", title="Target Label Distribution")
                        st.plotly_chart(fig1, use_container_width=True)

                    # 2. Source-wise Label Distribution
                    if "source" in result_df.columns and "target_label" in result_df.columns:
                        fig2 = px.histogram(result_df, x="source", color="target_label",
                                        barmode="group", title="Source-wise Target Label Distribution")
                        st.plotly_chart(fig2, use_container_width=True)

                    # --- 3. Method Usage (LLM/Regex/BERT) ---
                    if "used_method" in result_df.columns:
                        fig3 = px.pie(result_df, names="used_method", title="Classification Method Usage")
                        st.plotly_chart(fig3, use_container_width=True)

                    # Confidence score histogram
                    if "confidence" in result_df.columns:
                        # Box plot of confidence per label
                        fig4 = px.box(result_df, x="target_label", y="confidence", color="target_label",
                                      title="Confidence by Label")
                        st.plotly_chart(fig4, use_container_width=True)

                    # Heatmap: Source vs Label
                    pivot = result_df.pivot_table(index="source", columns="target_label", aggfunc="size", fill_value=0)
                    st.subheader("🔥 Source vs Label Heatmap")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax)
                    st.pyplot(fig)

                    # --- 6. Top N Frequent Logs by Label ---
                    st.subheader("🔎 Top Frequent Logs by Label")
                    for label in result_df["target_label"].unique():
                        st.markdown(f"**Label: `{label}`**")
                        subset = result_df[result_df["target_label"] == label]
                        top_logs = subset["log_message"].value_counts().head(3)
                        for msg, count in top_logs.items():
                            st.markdown(f"- {msg} ({count} times)")

                    # --- Download Option ---
                    st.download_button("⬇️ Download Classified CSV",
                                       data=response.content,
                                       file_name="classified_logs.csv",
                                       mime="text/csv")
                else:
                    st.error(f"❌ Server error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"⚠️ Error processing file: {str(e)}")
