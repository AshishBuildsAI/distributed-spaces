import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, Button, ListGroup } from 'react-bootstrap';

const AdminPanel = ({ selectedSpace, selectedFile, setSelectedFile }) => {
    const [files, setFiles] = useState([]);

    useEffect(() => {
        if (selectedSpace) {
            fetchFiles(selectedSpace);
        }
    }, [selectedSpace]);

    const fetchFiles = async (space) => {
        const response = await axios.get(`http://127.0.0.1:5000/list_files/${space}`);
        setFiles(response.data.files);
    };

    const indexFile = async () => {
        if (selectedFile) {
            try {
                const response = await axios.post('http://127.0.0.1:5000/index_file', { 
                    space: selectedSpace, 
                    filename: selectedFile 
                });
                alert(response.data.message);
            } catch (error) {
                alert('Error indexing file');
            }
        } else {
            alert('No file selected');
        }
    };

    return (
        <Card className="admin-panel">
            <Card.Header>Admin Panel</Card.Header>
            <Card.Body>
                <h3>Files in {selectedSpace}</h3>
                <ListGroup>
                    {files.map((file, index) => (
                        <ListGroup.Item 
                            key={index} 
                            onClick={() => setSelectedFile(file)}
                            active={selectedFile === file}
                        >
                            {file}
                        </ListGroup.Item>
                    ))}
                </ListGroup>
                {selectedFile && (
                    <Button className="mt-2" onClick={indexFile}>Index this file</Button>
                )}
            </Card.Body>
        </Card>
    );
};

export default AdminPanel;
