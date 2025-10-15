import streamlit as st  # 导入Streamlit库，用于创建Web应用  
import time  # 导入time库，用于控制文本输出的速度   
import os
from openai import OpenAI 
# 设置Streamlit应用的标题和头部信息  
st.title(":shrimp: :rainbow[chatbot] :rainbow[聊天机器人] :eyes:")  
st.header(" :blue[_you could ask anything here_]", divider="rainbow")  

# 设置侧边栏标题  
st.sidebar.title("用户认证")  

# 预设的账号密码（在实际应用中应该使用更安全的方式存储）
CORRECT_USERNAME = "max"
CORRECT_PASSWORD = "123456"

# 初始化会话状态
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "messages" not in st.session_state:  
    st.session_state.messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手"}
    ]

# 认证函数
def authenticate():
    username = st.session_state.get("username_input", "")
    password = st.session_state.get("password_input", "")
    
    if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.rerun()
    else:
        st.session_state.authenticated = False
        st.sidebar.error("账号或密码错误！")

# 登出函数
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    if "username_input" in st.session_state:
        st.session_state.username_input = ""
    if "password_input" in st.session_state:
        st.session_state.password_input = ""
    st.rerun()

# 如果用户已认证，显示聊天界面
if st.session_state.authenticated:
    st.text("使用deepseek模型-提问内容不限")  
    # 显示安全提示文本区域  
    st.text_area("安全提示", "请确保您的问题合法、合规且合理...")  
    
    # 显示用户信息和登出按钮
    st.sidebar.success(f"已登录为: {st.session_state.username}")
    if st.sidebar.button("登出"):
        logout()
    
    # 创建一个单选按钮，用于收集用户对回答的评价  
    select = st.sidebar.radio("你觉得回答有用吗？", ["有用", "无用", "有点用"], captions=["值得鼓励", "需要提升", "继续努力"])  
    st.sidebar.write("you selected:", select)  
    
    # 添加清除聊天历史按钮
    if st.sidebar.button("清除聊天记录"):
        st.session_state.messages = [
            {"role": "system", "content": "你是一个有帮助的AI助手"}
        ]
        st.rerun()
    
    # 显示之前的聊天消息  
    for message in st.session_state.messages:
        if message["role"] != "system":  # 不显示系统消息
            with st.chat_message(message["role"]):  
                st.markdown(message["content"])  
    
    # 获取用户的输入  
    prompt = st.chat_input("在这里提问")  
    
    # 如果用户输入了内容  
    if prompt:  
        # 将用户消息添加到聊天历史记录中  
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 在聊天消息容器中显示用户消息  
        with st.chat_message("user"):  
            st.markdown(prompt)  
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 初始化OpenAI客户端
            api = 'sk-caa08ff7e9c64786b45e9b98ec281ee1'
            client = OpenAI(
                api_key=api,
                base_url="https://api.deepseek.com"
            )
            
            try:
                # 调用API
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=st.session_state.messages,
                    stream=True
                )
                
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        chunk_content = chunk.choices[0].delta.content
                        full_response += chunk_content
                        message_placeholder.markdown(full_response + "▌")
                
                # 显示最终结果
                message_placeholder.markdown(full_response)
                
                # 将完整回复添加到消息历史
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_message = f"抱歉，发生错误: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# 如果用户未认证，显示登录界面
else:
    st.warning("请先登录以使用聊天功能")
    
    # 在侧边栏显示登录表单
    st.sidebar.subheader("登录")
    
    # 使用表单来组织登录输入
    with st.sidebar.form("login_form"):
        username = st.text_input("账号", key="username_input")
        password = st.text_input("密码", type="password", key="password_input")
        login_button = st.form_submit_button("登录", type="primary")
        
        if login_button:
            if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.sidebar.error("账号或密码错误！")
    
    # 显示帮助信息
    st.sidebar.info(f"请输入账号密码后再使用")
    
    # 提供一个链接按钮，用于获取API密钥  
    st.sidebar.link_button("获取API密钥", "https://platform.deepseek.com/api_keys")
