import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Form, Button, ProgressBar, ListGroup } from 'react-bootstrap';
import './SpaceExplorer.css'; // Ensure this file exists and is correctly imported

const SpaceExplorer = ({ setSelectedFile, setSelectedSpace, selectedFile }) => {
    const [spaces, setSpaces] = useState([]);
    const [file, setFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const fileInputRef = useRef(null);
    const [selectedSpaceState, setSelectedSpaceState] = useState(null);

    const fetchSpaces = useCallback(async () => {
        try {
            const response = await axios.get('http://127.0.0.1:5000/list_spaces');
            console.log('Spaces API response:', response.data); // Log the response

            const spacesData = response.data.spaces;
            if (Array.isArray(spacesData)) {
                const spaceObjects = await Promise.all(
                    spacesData.map(async (spaceName) => {
                        const filesResponse = await axios.get(`http://127.0.0.1:5000/list_files/${spaceName}`);
                        console.log(`Files in ${spaceName}:`, filesResponse.data.files); // Log the files response
                        return { name: spaceName, files: filesResponse.data.files };
                    })
                );
                setSpaces(spaceObjects);
                console.log('Space objects:', spaceObjects); // Log the space objects
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

    const fetchFiles = useCallback((space) => {
        setSelectedSpace(space); // Update the selected space in App component
        setSelectedSpaceState(space); // Update local state
        setSelectedFile(null); // Clear selected file when space is changed
    }, [setSelectedSpace, setSelectedFile]);

    const uploadFile = async () => {
        if (file && selectedSpaceState) {
            if (file.type !== 'application/pdf') {
                alert('Only PDF files are allowed');
                return;
            }
            const formData = new FormData();
            formData.append('file', file);
            try {
                const response = await axios.post(`http://127.0.0.1:5000/upload_file/${selectedSpaceState.name}`, formData, {
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
                        active={selectedSpaceState && selectedSpaceState.name === space.name}
                    >
                        {space.name} ({space.files.length} files)
                    </ListGroup.Item>
                ))}
            </ListGroup>
            {selectedSpaceState && (
                <Form className="upload-form mt-3">
                    <Form.Group controlId="formFile" className="mb-3">
                        <Form.Label>Upload File</Form.Label>
                        <Form.Control 
                            type="file" 
                            accept="application/pdf"
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
