import React, { useState } from 'react';
import axios from 'axios';
import { Form, Button, InputGroup } from 'react-bootstrap';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const CreateSpace = ({ fetchSpaces }) => {
    const [spaceName, setSpaceName] = useState('');

    const createSpace = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/create_space', { spaceName });
            toast.success(response.data.message, {
                position: "top-center",
                autoClose: 5000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });
            setSpaceName(''); // Clear the input field after successful creation
            fetchSpaces(); // Refresh the list of spaces
        } catch (error) {
            toast.error(error.message + {
                position: "top-center",
                autoClose: 5000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
            });
        }
    };

    return (
        <div>
            <Form className="create-space-form">
                <InputGroup>
                    <Form.Control 
                        type="text" 
                        placeholder="Enter space name" 
                        value={spaceName} 
                        onChange={(e) => setSpaceName(e.target.value)} 
                    />
                    <Button variant="primary" onClick={createSpace}>Create Space</Button>
                </InputGroup>
            </Form>
            <ToastContainer />
        </div>
    );
};

export default CreateSpace;
