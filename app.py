import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Supported Indian languages
LANGUAGES = {
    'English': 'en',
    'Hindi': 'hi',
    'Telugu': 'te',
    'Tamil': 'ta',
    'Bengali': 'bn',
    'Marathi': 'mr',
    'Gujarati': 'gu',
    'Kannada': 'kn',
    'Malayalam': 'ml',
    'Punjabi': 'pa'
}

# Initialize session state
if 'report_chat_history' not in st.session_state:
    st.session_state.report_chat_history = []
if 'skin_chat_history' not in st.session_state:
    st.session_state.skin_chat_history = []
if 'report_analysis' not in st.session_state:
    st.session_state.report_analysis = None
if 'skin_analysis' not in st.session_state:
    st.session_state.skin_analysis = None
if 'uploaded_report_image' not in st.session_state:
    st.session_state.uploaded_report_image = None
if 'uploaded_skin_image' not in st.session_state:
    st.session_state.uploaded_skin_image = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Page configuration
st.set_page_config(
    page_title="Medical Assistant Bot",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        padding: 0.5rem 1rem;
        font-size: 1.1rem;
    }
    .analysis-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-top: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
def save_user_data(user_id, name, age, gender, report_type, analysis, timestamp):
    """Save user data to JSON file"""
    data_file = 'user_medical_data.json'
    
    # Load existing data
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = []
    else:
        all_data = []
    
    # Create new entry
    user_entry = {
        'user_id': user_id,
        'name': name,
        'age': age,
        'gender': gender,
        'report_type': report_type,
        'analysis': analysis,
        'timestamp': timestamp
    }
    
    all_data.append(user_entry)
    
    # Save to file
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

def display_chat_history(chat_history):
    """Display chat messages"""
    for message in chat_history:
        if message['role'] == 'user':
            st.markdown(f'<div class="chat-message user-message">👤 <strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message">🤖 <strong>Assistant:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏥 Medical Assistant Bot</h1>', unsafe_allow_html=True)
st.markdown("### Powered by Google Gemini 2.0 Flash")

# Sidebar for language selection and user info
with st.sidebar:
    st.header("⚙️ Settings")
    selected_language = st.selectbox(
        "Select Language / भाषा चुनें",
        options=list(LANGUAGES.keys()),
        index=0
    )
    
    st.markdown("---")
    st.header("👤 User Information")
    user_name = st.text_input("Name / नाम", placeholder="Enter your name")
    user_age = st.number_input("Age / उम्र", min_value=1, max_value=120, value=25)
    user_gender = st.selectbox("Gender / लिंग", ["Male", "Female", "Other"])
    
    st.markdown("---")
    st.markdown("### 📋 Features")
    st.markdown("""
    - 💬 Medical Query Summarization
    - 📄 Medical Report Analysis + Chat
    - 🔍 Skin Disease Detection + Chat
    - 🌐 Multilingual Support
    - 💾 Data Storage
    """)
    
    st.markdown("---")
    st.warning("⚠️ **Disclaimer**: This is an AI assistant and not a replacement for professional medical advice.")

# Main content tabs
tab1, tab2, tab3 = st.tabs(["💬 Medical Queries", "📄 Report Analysis", "🔍 Skin Disease Detection"])

# Tab 1: Medical Query Summarization
with tab1:
    st.header("Medical Query Summarization")
    st.write("Ask medical questions and get summarized, easy-to-understand answers.")
    
    query = st.text_area(
        "Enter your medical query:",
        placeholder="Example: What are the symptoms of diabetes? / मधुमेह के लक्षण क्या हैं?",
        height=150
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        summarize_btn = st.button("🔍 Summarize Query", key="summarize")
    
    if summarize_btn and query:
        with st.spinner("Analyzing your query..."):
            try:
                prompt = f"""You are an expert medical assistant. Analyze and summarize the following medical query 
                and provide a comprehensive, accurate, and easy-to-understand response in {selected_language} language.
                
                Structure your response as follows:
                1. **Understanding the Query**: Brief clarification of what's being asked
                2. **Key Information**: Main facts and important points (3-5 bullet points)
                3. **Detailed Explanation**: Comprehensive explanation in simple terms
                4. **Important Considerations**: Things to keep in mind
                5. **When to Seek Medical Help**: Red flags or situations requiring immediate attention
                6. **Recommendation**: Always advise consulting healthcare professionals
                
                Query: {query}
                
                Provide the complete response in {selected_language} language with clear formatting."""
                
                response = model.generate_content(prompt)
                # Save user data for medical query
                if user_name:
                    save_user_data(
                        user_id=st.session_state.user_id,
                        name=user_name,
                        age=user_age,
                        gender=user_gender,
                        report_type="Medical Query",
                        analysis=f"Query: {query}\n\nResponse: {response.text}",
                        timestamp=datetime.now().isoformat()
                    )
                
                
                st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
                st.success("✅ Summary Generated Successfully")
                st.markdown("### 📋 Medical Query Response:")
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Please check your GEMINI_API_KEY in the .env file")

# Tab 2: Medical Report Analysis with Chat
with tab2:
    st.header("📄 Medical Report Analysis")
    st.write("Upload medical report images and chat about your report for detailed insights.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("📸 **Tip**: Upload clear, high-resolution images for best results")
        uploaded_file = st.file_uploader(
            "Upload Medical Report Image",
            type=['png', 'jpg', 'jpeg'],
            help="Upload lab results, X-rays, CT scans, MRI reports, or any medical document",
            key="report_uploader"
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            max_display_size = (400, 400)
            image.thumbnail(max_display_size, Image.Resampling.LANCZOS)
            st.image(image, caption="Uploaded Medical Report", use_column_width=True)
            
            # Store the uploaded image in session state
            st.session_state.uploaded_report_image = Image.open(uploaded_file)
    
    with col2:
        if uploaded_file:
            analyze_btn = st.button("📊 Analyze Medical Report", key="analyze_report", use_container_width=True)
            
            if analyze_btn:
                with st.spinner("🔬 Analyzing medical report... Please wait..."):
                    try:
                        prompt = f"""You are an expert medical report analyzer. Carefully examine this medical report image 
                        and provide a comprehensive, detailed analysis in {selected_language} language.
                        
                        Provide your analysis in the following structured format:
                        
                        ## 📋 Report Type Identification
                        - Identify what type of medical report this is (Lab test, X-ray, CT scan, MRI, Prescription, etc.)
                        - Date of report (if visible)
                        - Issuing hospital/lab (if visible)
                        
                        ## 🔍 Detailed Findings
                        Extract and list ALL visible information:
                        - Test names with their values
                        - Normal reference ranges
                        - Units of measurement
                        - Any flags (High/Low/Critical)
                        
                        ## 📊 Parameter Analysis
                        For each test result, provide:
                        - What the test measures
                        - Normal range explanation
                        - Current value interpretation (Normal/Abnormal)
                        - Clinical significance
                        
                        ## 💡 Medical Interpretation
                        - What do these results indicate overall?
                        - Patterns or correlations between parameters
                        - Possible health implications
                        - Body systems affected
                        
                        ## ⚠️ Areas of Concern
                        - Any abnormal values requiring attention
                        - Severity of abnormalities (Mild/Moderate/Severe)
                        - Potential health risks
                        
                        ## 🏥 Recommendations
                        - Follow-up tests needed
                        - Lifestyle modifications
                        - Dietary suggestions
                        - When to consult doctor
                        
                        ## ⚡ Summary
                        Brief overall summary with key takeaways
                        
                        IMPORTANT: Be thorough and extract ALL visible information. Explain medical terms in simple language.
                        
                        Provide the complete analysis in {selected_language} language."""
                        
                        response = model.generate_content([prompt, st.session_state.uploaded_report_image])
                        
                        st.session_state.report_analysis = response.text
                        
                        # Save user data
                        if user_name:
                            save_user_data(
                                user_id=st.session_state.user_id,
                                name=user_name,
                                age=user_age,
                                gender=user_gender,
                                report_type="Medical Report",
                                analysis=response.text,
                                timestamp=datetime.now().isoformat()
                            )
                        
                        st.success("✅ Medical Report Analysis Complete")
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing report: {str(e)}")
    
    # Display analysis
    if st.session_state.report_analysis:
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("### 📊 Detailed Analysis Report:")
        st.markdown(st.session_state.report_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.warning("⚠️ **Medical Disclaimer**: This AI analysis is for informational purposes only.")
    
    # Chat section for medical report
    if st.session_state.uploaded_report_image and st.session_state.report_analysis:
        st.markdown("---")
        st.markdown("### 💬 Chat About Your Report")
        st.write("Ask follow-up questions about your medical report")
        
        # Display chat history
        display_chat_history(st.session_state.report_chat_history)
        
        # Chat input
        chat_col1, chat_col2 = st.columns([5, 1])
        with chat_col1:
            report_question = st.text_input(
                "Ask a question about your report:",
                key="report_chat_input",
                placeholder="e.g., What does my cholesterol level mean?"
            )
        with chat_col2:
            send_btn = st.button("Send", key="report_send", use_container_width=True)
        
        if send_btn and report_question:
            # Add user message to history
            st.session_state.report_chat_history.append({
                'role': 'user',
                'content': report_question
            })
            
            with st.spinner("Thinking..."):
                try:
                    chat_prompt = f"""You are a medical assistant helping explain a medical report. 
                    Previous analysis: {st.session_state.report_analysis}
                    
                    User question: {report_question}
                    
                    Provide a clear, detailed answer in {selected_language} language. 
                    Reference specific values from the report when relevant.
                    Be helpful and educational, but always remind users to consult healthcare professionals."""
                    
                    chat_response = model.generate_content([chat_prompt, st.session_state.uploaded_report_image])
                    
                    # Add assistant message to history
                    st.session_state.report_chat_history.append({
                        'role': 'assistant',
                        'content': chat_response.text
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.button("Clear Chat History", key="clear_report_chat"):
            st.session_state.report_chat_history = []
            st.rerun()

# Tab 3: Skin Disease Detection with Chat
with tab3:
    st.header("🔍 Skin Disease Detection")
    st.write("Upload an image of a skin condition and chat for detailed analysis.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("📸 **Photography Tips**: Take a well-lit, focused photo")
        skin_image = st.file_uploader(
            "Upload Skin Condition Image",
            type=['png', 'jpg', 'jpeg'],
            key="skin_upload",
            help="Upload a clear image of the skin condition"
        )
        
        if skin_image:
            image = Image.open(skin_image)
            max_display_size = (400, 400)
            image.thumbnail(max_display_size, Image.Resampling.LANCZOS)
            st.image(image, caption="Uploaded Skin Condition", use_column_width=True)
            
            # Store the uploaded image in session state
            st.session_state.uploaded_skin_image = Image.open(skin_image)
    
    with col2:
        if skin_image:
            detect_btn = st.button("🔬 Analyze Skin Condition", key="detect", use_container_width=True)
            
            if detect_btn:
                with st.spinner("🔬 Analyzing skin condition... Please wait..."):
                    try:
                        prompt = f"""You are an expert dermatology assistant. Carefully analyze this skin condition image 
                        and provide a comprehensive, detailed assessment in {selected_language} language.
                        
                        Provide your analysis in the following structured format:
                        
                        ## 👁️ Visual Characteristics
                        - Color (redness, darkening, discoloration)
                        - Texture (smooth, rough, scaly, bumpy)
                        - Pattern (circular, linear, clustered, widespread)
                        - Size and shape
                        - Location on body (if identifiable)
                        - Any lesions, bumps, blisters, or rashes
                        
                        ## 🔍 Possible Conditions (Differential Diagnosis)
                        List 3-5 possible conditions with detailed explanations:
                        1. Most likely condition - explain why
                        2. Second possibility - reasoning
                        3. Other potential conditions
                        
                        ## 📊 Severity Assessment
                        - Mild / Moderate / Severe (with justification)
                        - Progression indicators
                        - Complications to watch for
                        
                        ## 💊 General Care Recommendations
                        - Immediate care steps
                        - Things to avoid
                        - Over-the-counter options
                        - Home remedies
                        
                        ## 🚨 When to Seek Immediate Medical Attention
                        - Red flags requiring urgent care
                        - Signs of infection
                        - Severe symptoms
                        
                        ## 🏥 Medical Consultation Recommendations
                        - Why professional diagnosis is essential
                        - What type of specialist to see
                        - What tests might be needed
                        
                        CRITICAL: Always emphasize this is NOT a definitive diagnosis.
                        
                        Provide the complete analysis in {selected_language} language."""
                        
                        response = model.generate_content([prompt, st.session_state.uploaded_skin_image])
                        
                        st.session_state.skin_analysis = response.text
                        
                        # Save user data
                        if user_name:
                            save_user_data(
                                user_id=st.session_state.user_id,
                                name=user_name,
                                age=user_age,
                                gender=user_gender,
                                report_type="Skin Condition",
                                analysis=response.text,
                                timestamp=datetime.now().isoformat()
                            )
                        
                        st.success("✅ Skin Condition Analysis Complete")
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing skin condition: {str(e)}")
    
    # Display analysis
    if st.session_state.skin_analysis:
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("### 🔬 Detailed Dermatological Assessment:")
        st.markdown(st.session_state.skin_analysis)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.error("🚨 **IMPORTANT**: This AI analysis is NOT a medical diagnosis. Consult a dermatologist.")
    
    # Chat section for skin condition
    if st.session_state.uploaded_skin_image and st.session_state.skin_analysis:
        st.markdown("---")
        st.markdown("### 💬 Chat About Your Skin Condition")
        st.write("Ask follow-up questions about the analysis")
        
        # Display chat history
        display_chat_history(st.session_state.skin_chat_history)
        
        # Chat input
        chat_col1, chat_col2 = st.columns([5, 1])
        with chat_col1:
            skin_question = st.text_input(
                "Ask a question about your skin condition:",
                key="skin_chat_input",
                placeholder="e.g., How long will this take to heal?"
            )
        with chat_col2:
            send_btn2 = st.button("Send", key="skin_send", use_container_width=True)
        
        if send_btn2 and skin_question:
            # Add user message to history
            st.session_state.skin_chat_history.append({
                'role': 'user',
                'content': skin_question
            })
            
            with st.spinner("Thinking..."):
                try:
                    chat_prompt = f"""You are a dermatology assistant helping explain a skin condition analysis. 
                    Previous analysis: {st.session_state.skin_analysis}
                    
                    User question: {skin_question}
                    
                    Provide a clear, detailed answer in {selected_language} language. 
                    Reference specific observations from the analysis when relevant.
                    Be helpful and educational, but always remind users to consult a dermatologist."""
                    
                    chat_response = model.generate_content([chat_prompt, st.session_state.uploaded_skin_image])
                    
                    # Add assistant message to history
                    st.session_state.skin_chat_history.append({
                        'role': 'assistant',
                        'content': chat_response.text
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.button("Clear Chat History", key="clear_skin_chat"):
            st.session_state.skin_chat_history = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; padding: 2rem 0;'>
    <p style='font-size: 1.1rem;'><strong>🏥 Medical Assistant Bot | Powered by Google Gemini 2.0 Flash</strong></p>
    <p style='font-size: 0.9rem;'>Supports: English, Hindi, Telugu, Tamil, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi</p>
    <p style='font-size: 0.85rem; color: #d32f2f; font-weight: bold;'>⚠️ This tool is for informational purposes only.</p>
    <p style='font-size: 0.85rem;'>User data is stored locally in user_medical_data.json</p>
    </div>
""", unsafe_allow_html=True)