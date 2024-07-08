import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/cerulean/bootstrap.min.css'; // You can choose a different theme if you like

import React, { useState } from 'react';
import CreateSpace from './components/CreateSpace';
import SpaceExplorer from './components/SpaceExplorer';
import ChatBot from './components/ChatBot';
import AdminPanel from './components/AdminPanel';
import Footer from './components/Footer';
import { Container, Row, Col, Navbar } from 'react-bootstrap';
import './App.css'; // Import custom CSS for additional styling

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedSpace, setSelectedSpace] = useState(null);

    return (
        <div className="d-flex flex-column min-vh-100">
            <Navbar bg="primary" variant="dark">
                <Container>
                    <Navbar.Brand href="#">My App</Navbar.Brand>
                </Container>
            </Navbar>
            <Container className="app-container flex-grow-1 mt-4">
                <CreateSpace />
                <Row>
                    <Col md={3} className="sidebar">
                        <SpaceExplorer 
                            setSelectedFile={setSelectedFile} 
                            setSelectedSpace={setSelectedSpace} 
                            selectedFile={selectedFile}
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
            <Footer />
        </div>
    );
}

export default App;
