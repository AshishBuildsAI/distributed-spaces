import React, { useState } from 'react';
import axios from 'axios';
import { Form, Button, InputGroup } from 'react-bootstrap';

const CreateSpace = () => {
    const [spaceName, setSpaceName] = useState('');

    const createSpace = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/create_space', { spaceName });
            alert(response.data.message);
        } catch (error) {
            alert('Error creating space');
        }
    };

    return (
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
    );
};

export default CreateSpace;
