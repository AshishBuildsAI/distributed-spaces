import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/darkly/bootstrap.min.css'; // You can choose a different theme if you like

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import CreateSpace from './components/CreateSpace';
import SpaceExplorer from './components/SpaceExplorer';
import ChatBot from './components/ChatBot';
import AdminPanel from './components/AdminPanel';
import Footer from './components/Footer';
import { Container, Row, Col } from 'react-bootstrap';
import './App.css'; // Import custom CSS for additional styling
import Space from './models/Space'; // Import the Space class

function App() {
    const [spaces, setSpaces] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedSpace, setSelectedSpace] = useState(null);

    const fetchSpaces = useCallback(async () => {
        try {
            const response = await axios.get('http://192.168.1.3:5000/list_spaces');
            const spacesData = response.data.spaces;
            if (Array.isArray(spacesData)) {
                const spaceObjects = await Promise.all(
                    spacesData.map(async (spaceName) => {
                        const filesResponse = await axios.get(`http://192.168.1.3:5000/list_files/${spaceName}`);
                        const files = filesResponse.data.files.map(file => ({
                            name: file.name,
                            isIndexed: file.isIndexed
                        }));
                        return new Space(spaceName, files);
                    })
                );
                setSpaces(spaceObjects);
                if (spaceObjects.length > 0) {
                    setSelectedSpace(spaceObjects[0]);
                }
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
            <Container fluid className="app-container flex-grow-1 mt-4">
                <CreateSpace fetchSpaces={fetchSpaces} />
                <Row>
                    <Col md={3} className="sidebar">
                        <SpaceExplorer
                            spaces={spaces}
                            setSelectedFile={setSelectedFile}
                            setSelectedSpace={setSelectedSpace}
                            selectedFile={selectedFile}
                            selectedSpace={selectedSpace}
                        />
                        <AdminPanel
                            spaces={spaces}
                            setSelectedFile={setSelectedFile}
                            setSelectedSpace={setSelectedSpace}
                            selectedFile={selectedFile}
                            selectedSpace={selectedSpace}
                        />
                    </Col>
                    <Col md={9} className="chat-panel">
                        <ChatBot selectedSpace={selectedSpace} selectedFile={selectedFile} />
                    </Col>
                </Row>
            </Container>
            <Footer />
        </div>
    );
}

export default App;
