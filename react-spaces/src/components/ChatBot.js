import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Card, ListGroup, Form, Button, InputGroup, Image, Spinner } from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';

const ChatBot = ({ selectedSpace, selectedFile }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isSending, setIsSending] = useState(false);
    const chatListRef = useRef(null);

    const sendMessage = async () => {
        if (!input.trim() || !selectedSpace || !selectedFile) {
            alert("Please provide a message, select a space, and select a file.");
            return;
        }

        if (messages.length > 0 && messages[messages.length - 1].text === input.trim()) {
            alert("Please do not send the same message repeatedly.");
            return;
        }

        const userMessage = { sender: 'user', text: input.trim() };
        setMessages([...messages, userMessage]);
        setIsSending(true);

        console.log('Sending message:', userMessage); // Debug log

        try {
            const response = await axios.post(
                'http://127.0.0.1:5000/chat', // URL to the Flask backend
                { 
                    space: selectedSpace.name, 
                    filename: selectedFile.name, 
                    query: input.trim() 
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );
            // alert(response.data);
            console.log('API response:', response); // Debug log
            const botMessage = { sender: 'bot', text: response.data };
            setMessages(prevMessages => [...prevMessages, botMessage]);
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = { sender: 'bot', text: 'Error processing your request.' };
            setMessages(prevMessages => [...prevMessages, errorMessage]);
        } finally {
            setInput('');
            setIsSending(false);
        }
    };

    useEffect(() => {
        if (chatListRef.current) {
            chatListRef.current.scrollTop = chatListRef.current.scrollHeight;
        }
    }, [messages]);

    return (
        <Card className="chat-panel">
            <Card.Header>
                Chat With Your Documentation - {selectedSpace ? selectedSpace.name : 'No Space Selected'} / {selectedFile ? selectedFile.name : 'No File Selected'}
            </Card.Header>
            <Card.Body style={{ display: 'flex', flexDirection: 'column', height: '70vh' }}>
                <ListGroup className="chat-list flex-grow-1" ref={chatListRef} style={{ overflowY: 'auto' }}>
                    {messages.map((message, index) => (
                        <ListGroup.Item
                            key={index}
                            className={`d-flex ${message.sender === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                        >
                            {message.sender === 'bot' && (
                                <Image src="./bot_avatar.png" roundedCircle style={{ width: '30px', height: '30px', marginRight: '10px' }} />
                            )}
                            <div>
                             <span style={{ whiteSpace: 'pre-wrap' }}>
                                {message.sender === 'bot' ? (
                                    <ReactMarkdown>{message.text}</ReactMarkdown>
                                ) : (
                                    <p class="text-success">{message.text}</p>
                                )}
                            </span>
                            </div>
                            {message.sender === 'user' && (
                                <Image src="./user_avatar.png" roundedCircle style={{ width: '30px', height: '30px', marginLeft: '10px' }} />
                            )}
                        </ListGroup.Item>
                    ))}
                </ListGroup>
                <InputGroup className="mt-3">
                    <Form.Control
                        type="text"
                        placeholder="Type a message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && !isSending && sendMessage()}
                        disabled={isSending}
                    />
                    <Button variant="primary" onClick={sendMessage} disabled={isSending}>Send</Button>
                    {isSending && <Spinner animation="border" role="status" className="ml-2">
                        <span className="sr-only">Loading...</span>
                    </Spinner>}
                </InputGroup>
            </Card.Body>
        </Card>
    );
};

export default ChatBot;
