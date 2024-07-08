class Space {
    constructor(name, files) {
        this.name = name;
        this.files = files.map(file => new File(file, name));
    }

    get totalFiles() {
        return this.files.length;
    }

    get indexedFiles() {
        return this.files.filter(file => file.isIndexed()).length;
    }

    get notIndexedFiles() {
        return this.totalFiles - this.indexedFiles;
    }
}

export default Space;
