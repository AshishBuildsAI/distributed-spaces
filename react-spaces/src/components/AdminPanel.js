import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, Button, ListGroup, Spinner, ProgressBar } from 'react-bootstrap';
import File from '../models/File';

const AdminPanel = ({ selectedSpace, selectedFile, setSelectedFile }) => {
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);

    const fetchFiles = useCallback(async (spaceName) => {
        try {
            const response = await axios.get(`http://127.0.0.1:5000/list_files/${spaceName}`);
            const files = response.data.files;
            if (Array.isArray(files)) {
                selectedSpace.files = files.map(file => new File(file.name, spaceName, file.isIndexed));
                setSelectedFile(null);
            } else {
                console.error('Expected files to be an array');
            }
        } catch (error) {
            console.error('Error fetching files:', error);
        }
    }, [setSelectedFile, selectedSpace]);

    useEffect(() => {
        if (selectedSpace) {
            fetchFiles(selectedSpace.name);
        }
    }, [selectedSpace, fetchFiles]);

    const convertPdf = async () => {
        if (selectedFile && selectedSpace) {
            setLoading(true);
            setProgress(0);
            try {
                const response = await axios.post(
                    `http://127.0.0.1:5000/convert_pdf/${selectedFile.name}`,
                    { space: selectedSpace.name },
                    {
                        onUploadProgress: (progressEvent) => {
                            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                            setProgress(percentCompleted);
                        }
                    }
                );
                alert(response.data.message);
            } catch (error) {
                alert('Error converting PDF');
            } finally {
                setLoading(false);
                fetchFiles(selectedSpace.name); // Refresh files to update indexed status
            }
        } else {
            alert('No file selected');
        }
    };

    return (
        <Card className="admin-panel">
            <Card.Header>Admin Panel</Card.Header>
            <Card.Body>
                {selectedSpace ? (
                    <>
                        <h3>Files in {selectedSpace.name}</h3>
                        <p>Total Files: {selectedSpace.files.length}</p>
                        <p>Indexed Files: {selectedSpace.files.filter(file => file.isIndexed).length}</p>
                        <p>Not Indexed Files: {selectedSpace.files.filter(file => !file.isIndexed).length}</p>
                        <ListGroup>
                            {selectedSpace.files.map((file, index) => (
                                <ListGroup.Item
                                    key={index}
                                    onClick={() => setSelectedFile(file)}
                                    active={selectedFile && selectedFile.name === file.name}
                                >
                                    {file.name} - {file.isIndexed ? <span class="badge bg-success">Indexed</span> : <span class="badge bg-warning">Not Indexed</span>}
                                </ListGroup.Item>
                            ))}
                        </ListGroup>
                    </>
                ) : (
                    <p>Please select a space to view files.</p>
                )}
                {selectedFile && (
                    <>
                        {selectedFile.isIndexed ? (
                             
                            <div class="alert alert-dismissible alert-success">
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            <strong>{selectedFile.name}</strong> is already indexed. <a href="#" class="alert-link">is already indexed</a>.
                            </div>
                        ) : (
                            <>
                                <Button className="mt-2" onClick={convertPdf} variant="primary" disabled={loading}>
                                    {loading ? (
                                        <>
                                            <Spinner
                                                as="span"
                                                animation="border"
                                                size="sm"
                                                role="status"
                                                aria-hidden="true"
                                            /> Converting...
                                        </>
                                    ) : (
                                        'Index this file'
                                    )}
                                </Button>
                                {loading && (
                                    <ProgressBar now={progress} label={`${progress}%`} className="mt-3" />
                                )}
                            </>
                        )}
                    </>
                )}
            </Card.Body>
        </Card>
    );
};

export default AdminPanel;
