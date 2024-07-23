import React, { useState, useRef, useEffect } from 'react';
import { ListGroup, ProgressBar } from 'react-bootstrap';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './SpaceExplorer.css';
import { AiOutlineUpload } from 'react-icons/ai';

const SpaceExplorer = ({ spaces = [], setSelectedFile, setSelectedSpace, selectedFile }) => {
    const [file, setFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const fileInputRef = useRef(null);
    const [selectedSpaceState, setSelectedSpaceState] = useState(null);

    useEffect(() => {
        if (spaces.length > 0) {
            const firstSpace = spaces[0];
            setSelectedSpace(firstSpace);
            setSelectedSpaceState(firstSpace);
        }
    }, [spaces, setSelectedSpace]);

    const fetchFiles = (space) => {
        setSelectedSpace(space);
        setSelectedSpaceState(space);
        setSelectedFile(null);
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        if (selectedFile) {
            uploadFile(selectedFile);
        }
    };

    const uploadFile = async (file) => {
        if (file && selectedSpaceState) {
            if (file.type !== 'application/pdf') {
                toast.warn('Only PDF files are allowed');
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
                toast.success(response.data.message, {
                    position: "top-center",
                    autoClose: 2000,
                    hideProgressBar: false,
                    closeOnClick: true,
                    pauseOnHover: false,
                    draggable: false,
                    progress: undefined,
                });
                if (fileInputRef.current) {
                    fileInputRef.current.value = ''; // Clear file input
                }
                setFile(null); // Clear file state
                setUploadProgress(0); // Reset upload progress

                // Refresh file list after successful upload
                fetchFiles(selectedSpaceState);
            } catch (error) {
                toast.error('Error uploading file');
            }
        } else {
            toast.error('Please select a space and a file');
        }
    };

    return (
        <div className="admin-panel">
            <h5 className='text-info-emphasis'>Spaces</h5>
            <ListGroup className="list-group">
                {spaces.map((space, index) => (
                    <ListGroup.Item
                        className="list-group-item list-group-item-primary d-flex justify-content-between align-items-center"
                        key={index}
                        onClick={() => fetchFiles(space)}
                        active={selectedSpaceState && selectedSpaceState.name === space.name}
                    >
                        {space.name}
                        <span className="badge bg-warning rounded-pill">{space.files.filter(file => !file.isIndexed).length}</span>
                        <span className="badge bg-success rounded-pill">{space.files.filter(file => file.isIndexed).length}</span>
                        <span className="badge bg-primary rounded-pill">{space.files.length}</span>
                        <AiOutlineUpload onClick={(e) => { e.stopPropagation(); fileInputRef.current.click(); }} />
                    </ListGroup.Item>
                ))}
            </ListGroup>
            <input
                type="file"
                accept="application/pdf"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileChange}
            />
            {uploadProgress > 0 && (
                <ProgressBar now={uploadProgress} label={`${uploadProgress}%`} className="mt-3" />
            )}
            <ToastContainer />
        </div>
    );
};

export default SpaceExplorer;
