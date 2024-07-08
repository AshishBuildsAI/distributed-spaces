import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootswatch/dist/cerulean/bootstrap.min.css'; // You can choose a different theme if you like

import React, { useState } from 'react';
import CreateSpace from './components/CreateSpace';
import SpaceExplorer from './components/SpaceExplorer';
import ChatBot from './components/ChatBot';
import AdminPanel from './components/AdminPanel';
import Footer from './components/Footer';
import { Container, Grid, AppBar, Toolbar, Typography } from '@mui/material';
import './App.css'; // Import custom CSS for additional styling

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedSpace, setSelectedSpace] = useState(null);

    return (
        <div className="d-flex flex-column min-vh-100">
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6">My App</Typography>
                </Toolbar>
            </AppBar>
            <Container className="app-container flex-grow-1">
                <CreateSpace />
                <Grid container spacing={3}>
                    <Grid item md={3} className="sidebar">
                        <SpaceExplorer 
                            setSelectedFile={setSelectedFile} 
                            setSelectedSpace={setSelectedSpace} 
                            selectedFile={selectedFile}
                        />
                    </Grid>
                    <Grid item md={6} className="chat-panel">
                        <ChatBot 
                            selectedSpace={selectedSpace} 
                            selectedFile={selectedFile} 
                        />
                    </Grid>
                    <Grid item md={3} className="admin-panel">
                        <AdminPanel 
                            selectedSpace={selectedSpace} 
                            selectedFile={selectedFile} 
                            setSelectedFile={setSelectedFile} 
                        />
                    </Grid>
                </Grid>
            </Container>
            <Footer />
        </div>
    );
}

export default App;
