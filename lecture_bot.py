import streamlit as st

def lecture_bot_interface(model, transcript):
    st.sidebar.header("🤖 Lecture Chat Bot")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User input
    user_input = st.sidebar.text_input("Ask a question about the lecture:")

    # Send button
    if st.sidebar.button("Send"):
        if user_input.strip():
            st.session_state.chat_history.append({"role": "user", "message": user_input})

            # Build prompt context
            context = f"You are a helpful assistant. Answer questions based only on this lecture transcript:\n\n{transcript}\n\n"
            for chat in st.session_state.chat_history:
                context += f"{chat['role'].capitalize()}: {chat['message']}\n"

            # Generate response
            with st.sidebar.spinner("🤖 Bot is thinking..."):
                try:
                    response = model.generate_content(f"{context}\nBot:")
                    bot_message = response.text.strip()
                except Exception as e:
                    bot_message = f"❌ Error generating response: {e}"

            st.session_state.chat_history.append({"role": "bot", "message": bot_message})

    # Clear chat button
    if st.sidebar.button("🧹 Clear Chat"):
        st.session_state.chat_history = []

    # Display chat history
    if st.session_state.chat_history:
        st.sidebar.markdown("---")
        for chat in reversed(st.session_state.chat_history):
            role = "🧑 You" if chat["role"] == "user" else "🤖 Bot"
            st.sidebar.markdown(f"**{role}:** {chat['message']}")