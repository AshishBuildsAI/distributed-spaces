# distributed-spaces

**distributed-spaces** is an extension of the open-source Spaces RAG platform into a distributed multi-agent control and orchestration system. It adds support for agent messaging, coordination, and asynchronous task execution across multiple nodes.

## Features

*Creating a New Distributed Space*

- Easily create remote spaces (folders) to organize your documents.
- Upload documents to spaces for querying and interaction.
- **Multi-Agent Orchestration:**  
  Enables distributed coordination between AI agents via a custom protocol (DMCP) layered on top of the original Spaces API.

## Getting Started

- Node.js >= 18.x
- Install dependencies with `npm install`
- Run the development server with `npm start`

## Contributing

Contributions are welcome! Whether you're fixing bugs, improving documentation, or building new features — your input makes `distributed-spaces` better.

### How to Contribute

1. **Fork the Repository**  
   Click the "Fork" button on the top right and clone your fork locally.

2. **Create a Branch**  
   Use a descriptive branch name for your feature or fix:
   ```bash
   git checkout -b feature/agent-authentication
   ```

3. **Make Changes and Commit**  
   Follow clean code practices and write meaningful commit messages.
   ```bash
   git commit -m "Add agent authentication via token-based headers"
   ```

4. **Push and Open a Pull Request**  
   Push your branch to GitHub and open a PR against `main` with a clear description of your changes.

### Code Style

- Use `black` for Python formatting.
- Include type hints wherever possible.
- Comment agent interactions and message flows clearly.

### Issues and Feature Requests

Found a bug? Want a feature? Open an issue using the appropriate template and label it accordingly.

## Specification Reference

This project implements the [Distributed Multi-Agent Control Protocol (DMCP)](https://github.com/AshishBuildsAI/distributed-mcp), which defines the agent lifecycle, messaging formats, and orchestration logic used within `distributed-spaces`.

For details on the protocol, message schema, and coordination model, refer to the [DMCP Specification](https://github.com/AshishBuildsAI/distributed-mcp).

---
Let's build distributed intelligence together!