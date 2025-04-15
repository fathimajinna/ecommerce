import React, { useState, useRef, useEffect } from 'react';
import './chatbot.css'; // Import the CSS file

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const chatMessagesRef = useRef(null);

    const handleSendMessage = () => {
        if (inputText.trim()) {
            const newMessage = { text: inputText, sender: 'user' };
            setMessages(prevMessages => [...prevMessages, newMessage]);
            setInputText('');

            // Send the message to your backend API
            fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: inputText }),
            })
            .then(response => response.json())
            .then(data => {
                const botResponse = { text: data.response, sender: 'bot' };
                setMessages(prevMessages => [...prevMessages, botResponse]);
            })
            .catch(error => {
                console.error('Error:', error);
                const errorResponse = { text: "Sorry, I encountered an error.", sender: 'bot' };
                setMessages(prevMessages => [...prevMessages, errorResponse]);
            });
        }
    };

    const handleInputChange = (event) => {
        setInputText(event.target.value);
    };

    useEffect(() => {
        if (chatMessagesRef.current) {
            chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <div className="chatbot-container">
            <div className="chat-header">
                Ecommerce Assistant
            </div>
            <div className="chat-messages" ref={chatMessagesRef}>
                {messages.map((message, index) => (
                    <div key={index} className={`message ${message.sender}`}>
                        {message.text}
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={inputText}
                    onChange={handleInputChange}
                    placeholder="Type your message here..."
                    className="input-field"
                    onKeyPress={(event) => event.key === 'Enter' && handleSendMessage()}
                />
                <button onClick={handleSendMessage} className="send-button">
                    Send
                </button>
            </div>
        </div>
    );
};

export default Chatbot;