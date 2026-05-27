
                    with st.spinner("🔄 يقوم الذكاء الاصطناعي حالياً بقراءة البيانات وصياغة الخطط..."):
                        try:
                            genai.configure(api_key=api_key)
                            # تم تحديث النموذج هنا ليكون متوافقاً تماماً وبدون أخطاء مسافات
                            model = genai.GenerativeModel('gemini-1.5-flash')
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
