import fitz
from pathlib import Path
import os
class InputDocument:
    def __init__(self, document_name, file_path, save_images_to_disk=True):
        self.document_name = document_name
        self.pages = []
        space_path = Path(file_path).parent.absolute()
        self.file_path = file_path
        self.imagesfolder = os.path.join(space_path,self.document_name[0:self.document_name.rindex(".")] ) 
        if save_images_to_disk:
            if not os.path.exists(self.imagesfolder):
                if not os.path.exists(self.imagesfolder):
                    os.makedirs(self.imagesfolder)
                    print("Image folder path:", self.imagesfolder)
                    self.document = fitz.open(file_path)
                    self.total_pages = self.document.page_count
                    self.pages = [self.document.load_page(i).get_pixmap() for i in range(self.total_pages)]
                    self.current_page = 0
                    paths = self.save_pixmaps_to_images()
                    #return paths
        else:
            # document is already processed 
            return None

    def save_pixmaps_to_images(self):
        image_paths = []
        for i, pixmap in enumerate(self.pages):
            image_path = os.path.join(self.imagesfolder, f"page_{i+1}.png")
            pixmap.save(image_path)
            image_paths.append(image_path)
            print(f"Saved page {i+1} to {image_path}")
        return image_paths
    @property
    def extension(self):
        return self.document_name.split('.')[-1] if '.' in self.document_name else ''

    def get_current_page_pixmap(self):
        if 0 <= self.current_page < self.total_pages:
            return self.pages[self.current_page]
        else:
            return None

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        else:
            print("You are at the last page.")

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
        else:
            print("You are at the first page.")

    def go_to_page(self, page_number):
        if 0 <= page_number < self.total_pages:
            self.current_page = page_number
        else:
            print("Page number out of range.")


