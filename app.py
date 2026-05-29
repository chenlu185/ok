import streamlit as st
st.write(f"Streamlit 版本: {st.__version__}")
# 对话主界面
else:
    st.title("💬 与AI助手对话，创作宣传语")
    st.info("💡 提示：请至少进行3轮对话再提交数据")
    st.divider()

    # ===== 改用普通容器展示对话（完全避开 chat_message）=====
    chat_area = st.container()
    with chat_area:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div style='background-color:#e6f7ff; padding:10px; border-radius:10px; margin:5px 0'><b>🧑 你：</b><br>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color:#f6f6f6; padding:10px; border-radius:10px; margin:5px 0'><b>🤖 AI助手：</b><br>{msg['content']}</div>", unsafe_allow_html=True)
    
    # ===== 改用普通输入框 + 提交按钮（完全避开 chat_input）=====
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_area("请输入你的想法或指令……", key="user_message", height=100)
        col1, col2 = st.columns([1, 5])
        with col1:
            send_button = st.form_submit_button("📤 发送", use_container_width=True)
        
        if send_button and user_input and not st.session_state.submitted:
            # 添加用户消息
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.turn += 1
            
            # 调用 API
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            messages = [
                {
                    "role": "system",
                    "content": "你是广告文案助手，为高速速干吹风机创作宣传语，提供创意文案与修改建议。"
                }
            ]
            messages.extend(st.session_state.chat_history)
            
            post_data = {
                "model": MODEL_ID,
                "messages": messages,
                "temperature": 0.8
            }
            
            try:
                resp = requests.post(API_URL, headers=headers, json=post_data)
                resp.raise_for_status()
                res_json = resp.json()
                ai_text = res_json["choices"][0]["message"]["content"]
            except Exception as e:
                ai_text = f"调用异常：{str(e)}"
            
            st.session_state.chat_history.append({"role": "assistant", "content": ai_text})
            st.rerun()

    st.divider()
    current_turn = st.session_state.turn
    if current_turn >= 3:
        st.success(f"✅ 已完成 {current_turn} 轮对话，可提交数据")
        if st.button("📥 提交本次实验数据", type="primary"):
            dialog_content = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history])
            save_data = {
                "user_id": st.session_state.user_id,
                "turns": current_turn,
                "dialog": dialog_content,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            df = pd.DataFrame([save_data])
            df.to_csv(f"hairdryer_{st.session_state.user_id}.csv", index=False, encoding="utf-8-sig")
            st.session_state.submitted = True
            st.balloons()
            st.success("✅ 数据保存成功！")
    else:
        st.info(f"💬 当前轮次：{current_turn} / 至少需要3轮")
        st.warning("请继续对话")