class File {
    constructor(name, spaceName, isIndexed) {
        this.name = name;
        this.spaceName = spaceName;
        this.isIndexed = isIndexed;
        this.imagesFolder = `spaces/${this.spaceName}/${this.name}_images`;
    }
}

export default File;
