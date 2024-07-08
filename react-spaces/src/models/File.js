class File {
    constructor(name, spaceName) {
        this.name = name;
        this.spaceName = spaceName;
    }

    isIndexed() {
        // Check if the file is indexed by looking for the corresponding image folder
        // This is a placeholder implementation, replace it with actual logic to check if the file is indexed
        // For example, you might check if the folder exists on the server
        const imagesFolder = `uploads/${this.spaceName}/${this.name}_images`;
        // Implement logic to check if imagesFolder exists
        return false; // Replace with actual check
    }
}

export default File;