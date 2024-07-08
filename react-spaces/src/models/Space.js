import File from './File';

class Space {
    constructor(name, files = []) {
        this.name = name;
        this.files = files.map(file => new File(file.name, name, file.isIndexed));
    }
}

export default Space;
