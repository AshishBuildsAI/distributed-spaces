import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import "./Footer.css";
const Footer = () => {
    return (
        <footer className="bg-dark text-light  mt-auto sticky-footer">
            <Container>
                <Row>
                    <Col className="text-center">
                        Spaces Community Edition version 1.0, {new Date().getFullYear()}
                    </Col>
                </Row>
            </Container>
        </footer>
    );
};

export default Footer;
