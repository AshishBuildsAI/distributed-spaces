import React, { useState } from 'react';
import CreateSpace from './components/CreateSpace';
import SpaceExplorer from './components/SpaceExplorer';
import ChatBot from './components/ChatBot';
import AdminPanel from './components/AdminPanel';
import { Container, Row, Col } from 'react-bootstrap';
import './App.css'; // Import custom CSS for additional styling

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedSpace, setSelectedSpace] = useState(null);

    return (
        <Container fluid className="app-container">
            <CreateSpace />
            <Row>
                <Col md={3} className="sidebar">
                    <SpaceExplorer 
                        setSelectedFile={setSelectedFile} 
                        setSelectedSpace={setSelectedSpace} 
                    />
                </Col>
                <Col md={6} className="chat-panel">
                    <ChatBot 
                        selectedSpace={selectedSpace} 
                        selectedFile={selectedFile} 
                    />
                </Col>
                <Col md={3} className="admin-panel">
                    <AdminPanel 
                        selectedSpace={selectedSpace} 
                        selectedFile={selectedFile} 
                        setSelectedFile={setSelectedFile} 
                    />
                </Col>
            </Row>
        </Container>
    );
}

export default App;
