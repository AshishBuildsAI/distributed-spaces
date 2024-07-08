import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/darkly/bootstrap.min.css'; // You can choose a different theme if you like

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import CreateSpace from './components/CreateSpace';
import SpaceExplorer from './components/SpaceExplorer';
import ChatBot from './components/ChatBot';
import AdminPanel from './components/AdminPanel';
import Footer from './components/Footer';
import { Container, Row, Col, Navbar } from 'react-bootstrap';
import './App.css'; // Import custom CSS for additional styling

function App() {
    const [spaces, setSpaces] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedSpace, setSelectedSpace] = useState(null);

    const fetchSpaces = useCallback(async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/list_spaces');
            const spacesData = response.data.spaces;
            if (Array.isArray(spacesData)) {
                const spaceObjects = await Promise.all(
                    spacesData.map(async (spaceName) => {
                        const filesResponse = await axios.get(`http://127.0.0.1:5000/list_files/${spaceName}`);
                        return { name: spaceName, files: filesResponse.data.files };
                    })
                );
                setSpaces(spaceObjects);
                
                selectedSpace = spaceObjects[0]
            } else {
                console.error('Expected spaces to be an array');
            }
        } catch (error) {
            console.error('Error fetching spaces:', error);
        }
    }, []);

    useEffect(() => {
        fetchSpaces();
    }, [fetchSpaces]);

    return (
        <div className="d-flex flex-column min-vh-100">
            <Navbar bg="primary" variant="dark">
                <Container>
                    <Navbar.Brand href="#">My App</Navbar.Brand>
                </Container>
            </Navbar>
            <Container className="app-container flex-grow-1 mt-4">
                <CreateSpace fetchSpaces={fetchSpaces} />
                <Row>
                    <Col md={3} className="sidebar">
                        <SpaceExplorer 
                            spaces={spaces}
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
