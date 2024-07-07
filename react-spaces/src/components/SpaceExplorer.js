import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { ListGroup, Form, Button, ProgressBar, Card } from 'react-bootstrap';
import './SpaceExplorer.css'; // Ensure this file exists and is correctly imported
import 'bootswatch/dist/darkly/bootstrap.css'
const SpaceExplorer = ({ setSelectedFile, setSelectedSpace }) => {
    const [spaces, setSpaces] = useState([]);
    const [file, setFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const fileInputRef = useRef(null);
    const [selectedSpaceState, setSelectedSpaceState] = useState(null);

    useEffect(() => {
        fetchSpaces();
    }, []);

    const fetchSpaces = async () => {
        const response = await axios.get('http://127.0.0.1:5000/list_spaces');
        const spacesWithCounts = await Promise.all(response.data.spaces.map(async (space) => {
            const filesResponse = await axios.get(`http://127.0.0.1:5000/list_files/${space}`);
            return { name: space, fileCount: filesResponse.data.files.length };
        }));
        setSpaces(spacesWithCounts);
    };

    const fetchFiles = (space) => {
        setSelectedSpace(space.name); // Update the selected space in App component
        setSelectedSpaceState(space.name); // Update local state
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
                    onUploadProgress: (progressEvent) => {
                        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        setUploadProgress(percentCompleted);
                    },
                });
                alert(response.data.message);
                if (fileInputRef.current) {
                    fileInputRef.current.value = ''; // Clear file input
                }
                setFile(null); // Clear file state
                setUploadProgress(0); // Reset upload progress
                fetchSpaces(); // Refresh space list to update file counts
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
                        active={selectedSpaceState === space.name}
                    >
                        {space.name} ({space.fileCount} files)
                    </ListGroup.Item>
                ))}
            </ListGroup>
            {selectedSpaceState && (
                <Form className="upload-form mt-3">
                    <Form.Group controlId="formFile" className="mb-3">
                        <Form.Label>Upload File</Form.Label>
                        <Form.Control 
                            type="file" 
                            onChange={(e) => setFile(e.target.files[0])}
                            ref={fileInputRef}
                        />
                    </Form.Group>
                    <Button onClick={uploadFile} variant="primary">Upload</Button>
                    {uploadProgress > 0 && (
                        <ProgressBar now={uploadProgress} label={`${uploadProgress}%`} className="mt-3" />
                    )}
                </Form>
            )}
        </div>
    );
};

export default SpaceExplorer;
