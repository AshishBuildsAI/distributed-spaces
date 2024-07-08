import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, Button, ListGroup, Spinner, ProgressBar } from 'react-bootstrap';
import File from '../models/File';

const AdminPanel = ({ selectedSpace, selectedFile, setSelectedFile }) => {
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);

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
            }
        } else {
            alert('No file selected');
        }
    };

    return (
        <Card className="admin-panel">
            <Card.Header>Files in {selectedSpace.name}</Card.Header>
            <Card.Body>
                {selectedSpace ? (
                    <>
                        <p class="badge bg-light">All Documents: {selectedSpace.files.length}</p>
                        <p class="badge bg-success">Indexed: {selectedSpace.files.filter(file => file.isIndexed).length}</p>
                        <p class="badge bg-warning">Not Indexed: {selectedSpace.files.filter(file => !file.isIndexed).length}</p>
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
                            <p>{selectedFile.name} is already indexed.</p>
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
