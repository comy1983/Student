import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import io

# إعداد الصفحة مباشرة باسم المكتبة الصريح
st.set_page_config(page_title="منصة تحليل بيانات الطالبات الذكية", layout="wide")

# التنسيق ودعم اللغة العربية
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
        
        with tab_data:
            st.header("📁 بيانات الجدول المرفوع")
            st.dataframe(df, use_container_width=True)
            st.metric(label="إجمالي عدد السجلات", value=str(df.shape))

        with tab_charts:
            st.header("📊 تحليل النتائج بيانيا (أعمدة تفاعلية)")
            if len(columns) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_axis = st.selectbox("اختر محور X (مثل: اسم الطالبة):", columns, index=0)
                with col2:
                    y_axis = st.selectbox("اختر محور Y (الدرجات أو التقييمات):", columns, index=min(1, len(columns)-1))
                
                fig = px.bar(df, x=x_axis, y=y_axis, title=f"تحليل {y_axis} بالنسبة إلى {x_axis}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ يجب أن يحتوي الملف على عمودين على الأقل.")

        with tab_ai:
            st.header("🤖 تحليل البيانات وتقديم خطط علاجية واثرائية")
            if not api_key:
                st.info("🔑 يرجى إدخال مفتاح Gemini API في الشريط الجانبي لتفعيل هذه الميزة.")
            else:
                data_summary = df.to_string(index=False)
                prompt = f"""
                أنت خبير تربوي ومحلل بيانات محترف. بناءً على بيانات الطالبات التالية المأخوذة من ملف إكسل:
                {data_summary}
                قم بتقديم تقرير تربوي شامل ومفصل باللغة العربية يحتوي على:
                1. تحليل عام لمستوى الطالبات.
                2. خطة علاجية واضحة للطالبات ضعيفات المستوى أو اللواتي يواجهن صعوبات.
                3. خطة إثرائية للطالبات المتفوقات والمميزات لتعزيز قدراتهن.
                يرجى جعل التوصيات عملية وقابلة للتطبيق مباشرة.
                """
                
                if st.button("🚀 تشغيل الذكاء الاصطناعي ومستشار البيانات"):
                    with st.spinner("🔄 يقوم الذكاء الاصطناعي حالياً بقراءة البيانات وصياغة الخطط التربوية..."):
                        try:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel('gemini-1.5-pro')
 

                            response = model.generate_content(prompt)
                            st.session_state['ai_report'] = response.text
                            st.success("✨ تم إنشاء الخطط بنجاح!")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"❌ تعذر تشغيل الذكاء الاصطناعي. تفاصيل النظام: {e}")

        with tab_swot:
            st.header("📈 تحليل نقاط القوة والضعف بيانيا")
            score_col = st.selectbox("اختر عمود الدرجات/التقييم لنقاط القوة والضعف:", columns)
            if pd.api.types.is_numeric_dtype(df[score_col]):
                max_score = float(df[score_col].max())
                passing_score = st.number_input("حدد درجة النجاح:", min_value=0.0, max_value=max_score, value=max_score*0.6)
                df['التصنيف'] = df[score_col].apply(lambda x: 'نقطة قوة' if x >= passing_score else 'نقطة ضعف')
                fig_swot = px.pie(df, names='التصنيف', title=f"توزيع مستويات الطالبات بناءً على {score_col}", color_discrete_sequence=['#4CAF50', '#FF5252'])
                st.plotly_chart(fig_swot, use_container_width=True)
            else:
                st.warning("⚠️ العمود المختار غير رقمي.")

        with tab_reports:
            st.header("💾 حفظ وتحميل تقارير الطالبات")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button(label="📥 تحميل جدول البيانات المصنف (Excel)", data=buffer.getvalue(), file_name="تقرير_الطالبات_المصنف.xlsx", mime="application/vnd.ms-excel")
            if 'ai_report' in st.session_state:
                st.subheader("📄 تقرير الخطط:")
                st.download_button(label="📥 تحميل تقرير الخطط التربوية (TXT)", data=st.session_state['ai_report'], file_name="الخطط_العلاجية_والاثراية.txt", mime="text/plain")
    except Exception as e:
        st.error(f"❌ خطأ: {e}")
else:
    st.info("💡 في انتظار رفع ملف الإكسل لبدء التحليل الذكي...")
