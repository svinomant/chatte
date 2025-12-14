import streamlit as st
import datetime
import json
import os
from pathlib import Path

# Конфигурация страницы
st.set_page_config(
    page_title="Simple Chat",
    page_icon="💬",
    layout="wide"
)

# Файл для хранения сообщений
CHAT_FILE = "chat_history.json"


class SimpleChat:
    def __init__(self):
        self.init_session_state()
        self.load_messages()

    def init_session_state(self):
        """Инициализация состояния сессии"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        if 'user_name' not in st.session_state:
            st.session_state.user_name = ""

        if 'initialized' not in st.session_state:
            st.session_state.initialized = False

    def load_messages(self):
        """Загрузка истории сообщений из файла"""
        try:
            if os.path.exists(CHAT_FILE):
                with open(CHAT_FILE, 'r', encoding='utf-8') as f:
                    st.session_state.messages = json.load(f)
        except:
            st.session_state.messages = []

    def save_messages(self):
        """Сохранение сообщений в файл"""
        try:
            with open(CHAT_FILE, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        except:
            pass

    def add_message(self, sender, text):
        """Добавление нового сообщения"""
        message = {
            'sender': sender,
            'text': text,
            'time': datetime.datetime.now().strftime("%H:%M:%S"),
            'date': datetime.datetime.now().strftime("%Y-%m-%d")
        }
        st.session_state.messages.append(message)
        self.save_messages()

    def delete_message(self, index):
        """Удаление сообщения по индексу"""
        if 0 <= index < len(st.session_state.messages):
            st.session_state.messages.pop(index)
            self.save_messages()
            st.rerun()

    def clear_chat(self):
        """Очистка всего чата"""
        st.session_state.messages = []
        self.save_messages()
        st.rerun()


def main():
    st.title("💬 Простой чат-мессенджер")
    st.markdown("---")

    # Инициализация чата
    chat = SimpleChat()

    # Боковая панель для настроек
    with st.sidebar:
        st.header("Настройки чата")

        # Ввод имени пользователя
        st.session_state.user_name = st.text_input(
            "Ваше имя:",
            value=st.session_state.user_name if st.session_state.user_name else "",
            placeholder="Введите ваше имя"
        )

        if not st.session_state.user_name:
            st.warning("⚠️ Пожалуйста, введите имя перед отправкой сообщений")

        st.markdown("---")

        # Статистика
        st.subheader("📊 Статистика")
        st.write(f"**Всего сообщений:** {len(st.session_state.messages)}")

        if st.session_state.messages:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            today_messages = [m for m in st.session_state.messages if m['date'] == today]
            st.write(f"**Сегодня:** {len(today_messages)} сообщений")

        st.markdown("---")

        # Управление чатом
        st.subheader("🛠 Управление")

        if st.button("🗑 Очистить весь чат", type="secondary"):
            if st.session_state.messages:
                if st.checkbox("Подтвердить удаление всех сообщений"):
                    chat.clear_chat()
            else:
                st.info("Чат уже пуст")

        st.markdown("---")
        st.caption("💡 Сообщения сохраняются в файл и доступны после перезагрузки")

    # Основная область - отображение сообщений
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📨 Сообщения")

        # Отображение истории сообщений
        if not st.session_state.messages:
            st.info("👋 Чат пуст. Будьте первым, кто напишет сообщение!")
        else:
            for i, msg in enumerate(st.session_state.messages):
                # Определяем стиль сообщения
                is_current_user = msg['sender'] == st.session_state.user_name

                with st.container():
                    cols = st.columns([1, 20])

                    with cols[0]:
                        # Аватар
                        if is_current_user:
                            st.markdown("👤")
                        else:
                            st.markdown("🤖")

                    with cols[1]:
                        # Контейнер сообщения
                        with st.chat_message("user" if is_current_user else "assistant"):
                            st.markdown(f"**{msg['sender']}**")
                            st.write(msg['text'])
                            st.caption(f"🕐 {msg['time']} | 📅 {msg['date']}")

                            # Кнопка удаления для своих сообщений
                            if is_current_user:
                                if st.button("Удалить", key=f"del_{i}"):
                                    chat.delete_message(i)

                    st.markdown("---")

    # Панель ввода нового сообщения
    with col2:
        st.subheader("✏️ Новое сообщение")

        # Форма ввода
        with st.form(key="message_form", clear_on_submit=True):
            message_text = st.text_area(
                "Текст сообщения:",
                height=150,
                max_chars=500,
                placeholder="Введите ваше сообщение здесь..."
            )

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                submit_button = st.form_submit_button(
                    "📤 Отправить",
                    type="primary",
                    disabled=not st.session_state.user_name
                )

            with col_btn2:
                clear_button = st.form_submit_button("Очистить")

        # Обработка отправки сообщения
        if submit_button and message_text.strip():
            if st.session_state.user_name:
                chat.add_message(st.session_state.user_name, message_text.strip())
                st.success("✅ Сообщение отправлено!")
                st.rerun()
            else:
                st.error("❌ Введите имя перед отправкой сообщения")


if __name__ == "__main__":
    main()
