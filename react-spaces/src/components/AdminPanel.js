import React, { useState } from 'react';
import axios from 'axios';
import { Card, Button, ListGroup, Spinner, ProgressBar } from 'react-bootstrap';

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
            <Card.Header>Files in {selectedSpace ? selectedSpace.name:""}</Card.Header>
            <Card.Body>
                {selectedSpace ? (
                    <>
                        <p data-bs-toggle="tooltip" data-bs-placement="right" data-bs-original-title="Tooltip on right" className="badge bg-primary" >Total Files: {selectedSpace.files.length}</p>
                        <p className="badge bg-success">Indexed Files: {selectedSpace.files.filter(file => file.isIndexed).length}</p>
                        <p className="badge bg-warning">Not Indexed Files: {selectedSpace.files.filter(file => !file.isIndexed).length}</p>
                        <ListGroup className='list-group' style={{ display: 'flex', flexDirection: 'column', height: '85vh' }}>
                            {selectedSpace.files.map((file, index) => (
                                <ListGroup.Item
                                    className='list-group-item list-group-item-action flex-column align-items-start'
                                    key={index}
                                    onClick={() => setSelectedFile(file)}
                                    active={selectedFile && selectedFile.name === file.name}
                                >
                                    {file.name}{file.isIndexed ? <span className="badge rounded-pill bg-success">Indexed</span> : <span className="badge rounded-pill bg-warning">Not Indexed</span>}
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
                            
                            <p className='alert alert-dismissible alert-success'>{selectedFile.name} is already indexed.</p>
                        ) : (
                            <>
                                <Button className="mt-2 btn btn-warning" onClick={convertPdf} variant="primary" disabled={loading}>
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
