import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import io

# إعدادات الصفحة العامة للتطبيق
st.set_page_config(
    page_title="منصة تحليل بيانات الطالبات الذكية",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق تنسيق CSS لتحسين المظهر وجعل الواجهة تدعم اللغة العربية (RTL)
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
""", unsafe_allow_index=True)

st.title("📊 منصة تحليل بيانات الطالبات المدعومة بالذكاء الاصطناعي")
st.subheader("تحليل ذكي، خطط علاجية، وتقارير فورية لأي ملف إكسل")

# شريط جانبي لإعدادات الاتصال والملفات
with st.sidebar:
    st.header("⚙️ الإعدادات والملفات")
    
    # استقبال مفتاح الـ AI
    api_key = st.text_input("أدخل مفتاح Google Gemini API:", type="password")
    
    # استقبال أي ملف إكسل بدون صيغة محددة (xls أو xlsx)
    uploaded_file = st.file_uploader("قم برفع ملف الإكسل الخاص بالطالبات", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # قراءة ملف الإكسل تلقائياً
        df = pd.read_excel(uploaded_file)
        st.sidebar.success("✅ تم تحميل الملف بنجاح!")
        
        # عرض البيانات الأساسية في الشريط الجانبي للتأكيد
        with st.sidebar.expander("👀 معاينة البيانات السريعة"):
            st.write(df.head(3))
            
        # تحديد الأعمدة الديناميكية بناءً على ملف المستخدم
        columns = df.columns.tolist()
        
        # إنشاء الأيقونات التفاعلية في صورة علامات تبويب (Tabs)
        tab_data, tab_charts, tab_ai, tab_swot, tab_reports = st.tabs([
            "📁 استعراض البيانات", 
            "📊 تحليل النتائج (أعمدة)", 
            "🤖 مستشار الذكاء الاصطناعي", 
            "📈 نقاط القوة والضعف", 
            "💾 حفظ التقارير"
        ])
        
        # --- 1️⃣ أيقونة استعراض البيانات ---
        with tab_data:
            st.header("📁 بيانات الجدول المرفوع")
            st.dataframe(df, use_container_width=True)
            st.metric(label="إجمالي عدد السجلات (الطالبات/المواد)", value=df.shape[0])

        # --- 2️⃣ أيقونة تحليل النتائج في صورة أعمدة ---
        with tab_charts:
            st.header("📊 تحليل النتائج بيانيا (أعمدة تفاعلية)")
            if len(columns) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_axis = st.selectbox("اختر محور X (مثل: اسم الطالبة أو الصف):", columns, index=0)
                with col2:
                    y_axis = st.selectbox("اختر محور Y (الدرجات أو التقييمات):", columns, index=min(1, len(columns)-1))
                
                color_axis = st.selectbox("فرز الألوان حسب (اختياري):", ["بدون فرز"] + columns)
                
                color_param = None if color_axis == "بدون فرز" else color_axis
                
                fig = px.bar(df, x=x_axis, y=y_axis, color=color_param, title=f"تحليل {y_axis} بالنسبة إلى {x_axis}", barmode="group")
                fig.update_layout(xaxis_title=x_axis, yaxis_title=y_axis)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ يجب أن يحتوي الملف على عمودين على الأقل لإنشاء مخطط الأعمدة.")

        # --- 3️⃣ أيقونة مستشار الذكاء الاصطناعي (AI) ---
        with tab_ai:
            st.header("🤖 تحليل البيانات وتقديم خطط علاجية واثرائية")
            if not api_key:
                st.info("🔑 يرجى إدخال مفتاح Gemini API في الشريط الجانبي لتفعيل هذه الميزة.")
            else:
                # تحويل البيانات إلى نص ليقرأه الذكاء الاصطناعي
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
                
                if st.button("🚀 تشغيل الذكاء الاصطناعي وقراءة البيانات"):
                    with st.spinner("🔄 يقوم الذكاء الاصطناعي حالياً بقراءة البيانات وصياغة الخطط..."):
                        try:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel('gemini-pro')
                            response = model.generate_content(prompt)
                            
                            # حفظ نص الذكاء الاصطناعي في الـ session_state للاستفادة منه في قسم التقارير
                            st.session_state['ai_report'] = response.text
                            st.success("✨ تم إنشاء الخطط بنجاح!")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"❌ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")

        # --- 4️⃣ أيقونة نقاط القوة والضعف (مخطط بياني) ---
        with tab_swot:
            st.header("📈 تحليل نقاط القوة والضعف بيانيا")
            st.write("اختر عمود الدرجات لتحديد نقاط القوة (المتفوقات) ونقاط الضعف (بحاجة لدعم).")
            
            score_col = st.selectbox("اختر عمود الدرجات/التقييم لنقاط القوة والضعف:", columns, key="swot_col")
            
            # التحقق من أن العمود يحتوي على قيم رقمية لتصنيفها
            if pd.api.types.is_numeric_dtype(df[score_col]):
                max_score = float(df[score_col].max())
                passing_score = st.number_input("حدد درجة النجاح/الحد الفاصل لنقاط الضعف:", min_value=0.0, max_value=max_score, value=max_score*0.6)
                
                # تصنيف الطالبات
                df['التصنيف'] = df[score_col].apply(lambda x: 'نقطة قوة (متفوقة)' if x >= passing_score else 'نقطة ضعف (بحاجة لدعم)')
                
                # رسم مخطط دائري أو خطي يوضح النسب
                fig_swot = px.pie(df, names='التصنيف', title=f"توزيع نقاط القوة والضعف بناءً على {score_col}", color_discrete_sequence=['#4CAF50', '#FF5252'])
                st.plotly_chart(fig_swot, use_container_width=True)
                
                # عرض قوائم الطالبات لسهولة المتابعة
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("🟢 طالبات تمثل نقاط قوة")
                    st.dataframe(df[df['التصنيف'] == 'نقطة قوة (متفوقة)'][columns], use_container_width=True)
                with c2:
                    st.subheader("🔴 طالبات تمثل نقاط ضعف")
                    st.dataframe(df[df['التصنيف'] == 'نقطة ضعف (بحاجة لدعم)'][columns], use_container_width=True)
            else:
                st.warning("⚠️ العمود المختار غير رقمي. يرجى اختيار عمود يحتوي على درجات رقمية ليتم تحليلها.")

        # --- 5️⃣ أيقونة حفظ تقارير الطالبات ---
        with tab_reports:
            st.header("💾 حفظ وتحميل تقارير الطالبات")
            st.write("يمكنك تحميل البيانات الحالية بعد معالجتها وتصنيفها، أو نسخ تقرير الذكاء الاصطناعي.")
            
            # 1. تحميل ملف البيانات المعدل كـ Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='تقرير الطالبات')
            
            st.download_button(
                label="📥 تحميل جدول البيانات المصنف (Excel)",
                data=buffer.getvalue(),
                file_name="تقرير_الطالبات_المصنف.xlsx",
                mime="application/vnd.ms-excel"
            )
            
            # 2. تحميل تقرير الـ AI النصي إن وجد
            if 'ai_report' in st.session_state:
                st.subheader("📄 تقرير الخطط العلاجية والإثرائية الجاهز:")
                st.download_button(
                    label="📥 تحميل تقرير الخطط التربوية (TXT)",
                    data=st.session_state['ai_report'],
                    file_name="الخطط_العلاجية_والاثراية.txt",
                    mime="text/plain"
                )
            else:
                st.info("ℹ️ لطلب تحميل تقرير الخطط العلاجية، يرجى تشغيل مستشار الذكاء الاصطناعي أولاً من علامة التبويب الخاصة به.")

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء معالجة الملف، يرجى التأكد من صياغة جدول الإكسل بشكل صحيح. تفاصيل الخطأ: {e}")
else:
    st.info("💡 في انتظار رفع ملف الإكسل من الشريط الجانبي لبدء التحليل الذكي...")
