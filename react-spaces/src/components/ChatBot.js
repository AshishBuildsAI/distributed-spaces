import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Card, ListGroup, Form, Button, InputGroup, Image, Spinner, Dropdown, Modal } from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import { FaCog, FaCopy } from 'react-icons/fa';

const ChatBot = ({ selectedSpace, selectedFile }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isSending, setIsSending] = useState(false);
    const [selectedModel, setSelectedModel] = useState('llama3');
    const [showSettings, setShowSettings] = useState(false);
    const [showCopyButton, setShowCopyButton] = useState(true);
    const chatListRef = useRef(null);

    const sendMessage = async () => {
        if (!input.trim() || !selectedSpace) {
            alert("Please provide a message and select a space.");
            return;
        }

        if (messages.length > 0 && messages[messages.length - 1].text === input.trim()) {
            alert("Please do not send the same message repeatedly.");
            return;
        }

        const userMessage = { sender: 'user', text: input.trim() };
        setMessages([...messages, userMessage]);
        setIsSending(true);

        try {
            let payload = {
                space: selectedSpace.name,
                query: input.trim(),
                model: selectedModel
            };

            if (selectedFile) {
                payload.filename = selectedFile.name;
            }

            const response = await axios.post(
                'http://127.0.0.1:5000/chat', // URL to the Flask backend
                payload,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            const botMessageContent = response.data.content || 'No response';
            const botMessage = { sender: 'bot', text: botMessageContent };
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

    useEffect(() => {
        const handleScroll = () => {
            if (chatListRef.current) {
                const { scrollTop, scrollHeight, clientHeight } = chatListRef.current;
                const isAtBottom = scrollTop + clientHeight >= scrollHeight - 2;
                setShowCopyButton(isAtBottom);
            }
        };

        if (chatListRef.current) {
            chatListRef.current.addEventListener('scroll', handleScroll);
        }

        return () => {
            if (chatListRef.current) {
                chatListRef.current.removeEventListener('scroll', handleScroll);
            }
        };
    }, [messages]);

    const handleModelChange = (model) => {
        setSelectedModel(model);
    };

    const handleSettingsClose = () => setShowSettings(false);
    const handleSettingsShow = () => setShowSettings(true);

    const handleCopyToClipboard = (text) => {
        navigator.clipboard.writeText(text).then(() => {
            alert('Copied to clipboard');
        }).catch((err) => {
            console.error('Failed to copy text: ', err);
        });
    };

    return (
        <>
            <Card className="chat-panel">
                <Card.Header>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>
                            Chat With Your Documentation - {selectedSpace ? selectedSpace.name : 'No Space Selected'} / {selectedFile ? selectedFile.name : 'No File Selected'}
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            {isSending && <Spinner animation="border" size="sm" role="status" className="mr-2">
                                <span className="sr-only"></span>
                            </Spinner>}
                            <FaCog style={{ cursor: 'pointer' }} onClick={handleSettingsShow} />
                        </div>
                    </div>
                </Card.Header>
                <Card.Body style={{ display: 'flex', flexDirection: 'column', height: '85vh' }}>
                    <ListGroup className="chat-list flex-grow-1" ref={chatListRef} style={{ overflowY: 'auto' }}>
                        {messages.map((message, index) => (
                            <ListGroup.Item
                                key={index}
                                className={`d-flex ${message.sender === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                            >
                                {message.sender === 'bot' && (
                                    <Image src="./bot_avatar.png" roundedCircle style={{ width: '30px', height: '30px', marginRight: '10px' }} />
                                )}
                                <div style={{ position: 'relative', width: '100%' }}>
                                    <span style={{ whiteSpace: 'pre-wrap' }}>
                                        {message.sender === 'bot' ? (
                                            <ReactMarkdown>{message.text}</ReactMarkdown>
                                        ) : (
                                            <p className="text-warning">{message.text}</p>
                                        )}
                                    </span>
                                    {message.sender === 'bot' && showCopyButton && (
                                        <FaCopy
                                            style={{ position: 'absolute', top: 0, right: 0, cursor: 'pointer' }}
                                            onClick={() => handleCopyToClipboard(message.text)}
                                        />
                                    )}
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
                            placeholder="How may I help you?, built by DASCoE"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && !isSending && sendMessage()}
                            disabled={isSending}
                        />
                        <Button variant="primary" onClick={sendMessage} disabled={isSending}>Ask</Button>
                    </InputGroup>
                </Card.Body>
            </Card>

            <Modal show={showSettings} onHide={handleSettingsClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Settings</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form.Group controlId="modelSelect">
                        <Form.Label>Select Model</Form.Label>
                        <Dropdown onSelect={handleModelChange}>
                            <Dropdown.Toggle variant="success" id="dropdown-basic">
                                Model: {selectedModel}
                            </Dropdown.Toggle>

                            <Dropdown.Menu>
                                <Dropdown.Item eventKey="llama3">llama3</Dropdown.Item>
                                <Dropdown.Item eventKey="llama2">llama2</Dropdown.Item>
                                <Dropdown.Item eventKey="mistral">mistral</Dropdown.Item>
                                <Dropdown.Item eventKey="wizardlm2">wizardlm2</Dropdown.Item>
                                <Dropdown.Item eventKey="gemma2">gemma2</Dropdown.Item>
                                <Dropdown.Item eventKey="gpt-4o">Azure Open AI GPT-4o</Dropdown.Item>
                                <Dropdown.Item eventKey="gemini">Gemini</Dropdown.Item>
                            </Dropdown.Menu>
                        </Dropdown>
                    </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleSettingsClose}>
                        Close
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
};

export default ChatBot;
