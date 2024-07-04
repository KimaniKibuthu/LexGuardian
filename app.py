import streamlit as st
import io
import time
from contextlib import redirect_stdout
from lex_guardian.rag import (
    setup_environment,
    instantiate_db,
    setup_retriever,
    setup_llm,
    setup_rag_chain,
    stream_response,
)


def capture_stream_output(func, *args, **kwargs):
    output = io.StringIO()
    with redirect_stdout(output):
        func(*args, **kwargs)
    return output.getvalue()


def main():
    st.set_page_config(page_title="LexGuardian", page_icon="⚖️")
    st.title("LexGuardian - Your Pocket Lawyer")
    st.caption("Ask me anything about Kenyan law! ⚖️")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Initialize LexGuardian components
    if "rag_chain" not in st.session_state:
        with st.spinner("Getting my briefcase 🏃🏿‍♂️..."):
            config = setup_environment()
            vectorstore = instantiate_db(config)
            retriever = setup_retriever(vectorstore)
            llm = setup_llm()
            st.session_state.rag_chain = setup_rag_chain(retriever, llm)

    # Chat input
    if prompt := st.chat_input("Your question about Kenyan law"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                # Use the capture_stream_output function to get the streamed response
                with st.spinner("Racking my brain 🧐..."):
                    full_response = capture_stream_output(
                        stream_response,
                        query=prompt,
                        rag_chain=st.session_state.rag_chain,
                    )

                # Simulate streaming effect in Streamlit
                displayed_response = ""
                for (
                    chunk
                ) in full_response.split():  # Split by word for a smoother effect
                    displayed_response += chunk + " "
                    message_placeholder.markdown(displayed_response + "▌")
                    time.sleep(0.05)  # Adjust for desired speed

                message_placeholder.markdown(full_response)
            except Exception as e:
                error_message = f"I apologize, but I encountered an error while processing your question: {str(e)}"
                message_placeholder.markdown(error_message)
                full_response = error_message

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


if __name__ == "__main__":
    main()