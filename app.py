
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import io

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="منصة تحليل بيانات الطالبات الذكية",
    page_icon="📊",
    layout="wide"
)

# 2. التنسيق ودعم اللغة العربية
st.markdown("""
    <style>
    body { direction: rtl; text-align: right; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; direction: rtl; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #4CAF50; color: white; }
    div.stButton > button:first-child { background-color: #4CAF50; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 منصة تحليل بيانات الطالبات المدعومة بالذكاء الاصطناعي")
st.subheader("تحليل ذكي، خطط علاجية، وتقارير فورية لأي ملف إكسل")

# 3. شريط جانبي
with st.sidebar:
    st.header("⚙️ الإعدادات والملفات")
    api_key = st.text_input("أدخل مفتاح Google Gemini API:", type="password")
    uploaded_file = st.file_uploader("قم برفع ملف الإكسل الخاص بالطالبات", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ تم تحميل الملف بنجاح!")
        
        columns = df.columns.tolist()
        
        tab_data, tab_charts, tab_ai, tab_swot, tab_reports = st.tabs([
            "📁 استعراض البيانات", 
            "📊 تحليل النتائج (أعمدة)", 
            "🤖 مستشار الذكاء الاصطناعي", 
            "📈 نقاط القوة والضعف", 
            "💾 حفظ التقارير"
        ])
        
        # الأيقونة 1
        with tab_data:
            st.header("📁 بيانات الجدول المرفوع")
            st.dataframe(df, use_container_width=True)
            st.metric(label="إجمالي عدد السجلات", value=str(df.shape[0]))

        # الأيقونة 2
        with tab_charts:
            st.header("📊 تحليل النتائج بيانيا (أعمدة تفاعلية)")
            if len(columns) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_axis = st.selectbox("اختر محور X:", columns, index=0)
                with col2:
                    y_axis = st.selectbox("اختر محور Y:", columns, index=min(1, len(columns)-1))
                
                fig = px.bar(df, x=x_axis, y=y_axis, title=f"تحليل {y_axis} بالنسبة إلى {x_axis}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ يجب أن يحتوي الملف على عمودين على الأقل.")

        # الأيقونة 3
        with tab_ai:
            st.header("🤖 تحليل البيانات وتقديم خطط علاجية واثرائية")
            if not api_key:
                st.info("🔑 يرجى إدخال مفتاح Gemini API في الشريط الجانبي.")
            else:
                data_summary = df.to_string(index=False)
                prompt = f"أنت خبير تربوي. حلل هذه البيانات وقدم خطة علاجية لضعاف المستوى وإثرائية للمتفوقين:\n{data_summary}"
                
                if st.button("🚀 تشغيل الذكاء الاصطناعي"):
                    with st.spinner("🔄 جاري التحليل..."):
                        try:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                            response = model.generate_content(prompt)
                            st.session_state['ai_report'] = response.text
                            st.success("✨ تم إنشاء الخطط بنجاح!")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"❌ خطأ في الـ AI: {e}")

        # الأيقونة 4
        with tab_swot:
            st.header("📈 تحليل نقاط القوة والضعف بيانيا")
            score_col = st.selectbox("اختر عمود الدرجات:", columns)
            if pd.api.types.is_numeric_dtype(df[score_col]):
                max_score = float(df[score_col].max())
                passing_score = st.number_input("حدد درجة النجاح:", min_value=0.0, max_value=max_score, value=max_score*0.6)
                
                df['التصنيف'] = df[score_col].apply(lambda x: 'نقطة قوة' if x >= passing_score else 'نقطة ضعف')
                fig_swot = px.pie(df, names='التصنيف', title="توزيع مستويات الطالبات")
                st.plotly_chart(fig_swot, use_container_width=True)
            else:
                st.warning("⚠️ اختر عموداً رقمياً يحتوي على درجات.")

        # الأيقونة 5
        with tab_reports:
            st.header("💾 حفظ وتحميل تقارير الطالبات")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button(label="📥 تحميل جدول البيانات (Excel)", data=buffer.getvalue(), file_name="تقرير_الطالبات.xlsx", mime="application/vnd.ms-excel")
            
            if 'ai_report' in st.session_state:
                st.download_button(label="📥 تحميل تقرير الخطط (TXT)", data=st.session_state['ai_report'], file_name="الخطط_التربوية.txt", mime="text/plain")

    except Exception as e:
        st.error(f"❌ حدث خطأ في معالجة الملف: {e}")
else:
    st.info("💡 في انتظار رفع ملف الإكسل من الشريط الجانبي...")
