import React, { useState } from 'react';
import axios from 'axios';
import { Form, Button, InputGroup, Card, ListGroup } from 'react-bootstrap';
import './ChatBot.css'; // Ensure this file exists and is correctly imported

const ChatBot = ({ selectedSpace, selectedFile }) => {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);

    const askQuestion = async () => {
        const userMessage = { text: query, isUser: true };
        setMessages([...messages, userMessage]);

        try {
            const response = await axios.post('http://127.0.0.1:5000/chat', { 
                space: selectedSpace,
                query 
            });
            const botMessage = { text: response.data.response, isUser: false };
            setMessages([...messages, userMessage, botMessage]);
        } catch (error) {
            const errorMessage = { text: 'Error querying', isUser: false };
            setMessages([...messages, userMessage, errorMessage]);
        }

        setQuery('');
    };

    return (
        <Card className="chat-bot">
            <Card.Header>Chat Bot</Card.Header>
            <Card.Body className="chat-body">
                <ListGroup className="chat-list">
                    {messages.map((message, index) => (
                        <ListGroup.Item 
                            key={index} 
                            className={message.isUser ? 'user-message' : 'bot-message'}
                        >
                            {message.text}
                        </ListGroup.Item>
                    ))}
                </ListGroup>
                <InputGroup className="mt-3">
                    <Form.Control 
                        type="text" 
                        placeholder="Ask a question" 
                        value={query} 
                        onChange={(e) => setQuery(e.target.value)} 
                    />
                    <Button variant="primary" onClick={askQuestion}>Ask</Button>
                </InputGroup>
            </Card.Body>
        </Card>
    );
};

export default ChatBot;
