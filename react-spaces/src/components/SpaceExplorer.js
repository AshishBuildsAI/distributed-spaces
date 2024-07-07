import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { ListGroup, Form, Button } from 'react-bootstrap';
import './SpaceExplorer.css'; // Ensure this file exists and is correctly imported

const SpaceExplorer = ({ setSelectedFile, setSelectedSpace }) => {
    const [spaces, setSpaces] = useState([]);
    const [file, setFile] = useState(null);
    const fileInputRef = useRef(null);
    const [selectedSpaceState, setSelectedSpaceState] = useState(null);

    useEffect(() => {
        fetchSpaces();
    }, []);

    const fetchSpaces = async () => {
        const response = await axios.get('http://127.0.0.1:5000/list_spaces');
        setSpaces(response.data.spaces);
    };

    const fetchFiles = (space) => {
        setSelectedSpace(space); // Update the selected space in App component
        setSelectedSpaceState(space); // Update local state
        setSelectedFile(null); // Clear selected file when space is changed
    };

    const uploadFile = async () => {
        if (file && selectedSpaceState) {
            const formData = new FormData();
            formData.append('file', file);
            try {
                const response = await axios.post(`http://127.0.0.1:5000/upload_file/${selectedSpaceState}`, formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
                alert(response.data.message);
                if (fileInputRef.current) {
                    fileInputRef.current.value = ''; // Clear file input
                }
                setFile(null); // Clear file state
            } catch (error) {
                alert('Error uploading file');
            }
        } else {
            alert('Please select a space and a file');
        }
    };

    return (
        <div className="space-explorer">
            <h3>Spaces</h3>
            <ListGroup>
                {spaces.map((space, index) => (
                    <ListGroup.Item 
                        key={index} 
                        onClick={() => fetchFiles(space)}
                        active={selectedSpaceState === space}
                    >
                        {space}
                    </ListGroup.Item>
                ))}
            </ListGroup>
            {selectedSpaceState && (
                <Form className="upload-form">
                    <Form.Group controlId="formFile" className="mb-3">
                        <Form.Label>Upload File</Form.Label>
                        <Form.Control 
                            type="file" 
                            onChange={(e) => setFile(e.target.files[0])}
                            ref={fileInputRef}
                        />
                    </Form.Group>
                    <Button onClick={uploadFile}>Upload</Button>
                </Form>
            )}
        </div>
    );
};

export default SpaceExplorer;
