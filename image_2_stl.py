import numpy as np
from stl import mesh
from PIL import Image

def image_to_stl(image_path, stl_path, max_height=5, base_thickness=1):
    """
    Converts an image to a 3D STL file based on shadow (darker regions) for height mapping.
    
    :param image_path: Path to the input image
    :param stl_path: Path to the output STL file
    :param max_height: Maximum height (Z-axis) for the brightest areas
    :param base_thickness: Thickness of the base layer for stability
    """
    # Open the image and convert it to grayscale
    img = Image.open(image_path).convert("L")
    width, height = img.size
    pixels = np.array(img)

    # Invert pixel values so shadows become the basis for height
    inverted_pixels = 255 - pixels

    # Scale the inverted pixels to the max height
    scaled_pixels = (inverted_pixels / 255) * max_height

    # Create vertices and faces for the STL model
    vertices = []
    faces = []
    
    # Generate vertices with height based on inverted pixel value
    for y in range(height):
        for x in range(width):
            z = scaled_pixels[y, x]  # Height determined by shadow intensity
            vertices.append([x, y, z])  # Top surface vertices
            
            # Add base vertices for thickness
            vertices.append([x, y, -base_thickness])

    # Create faces for the top and base surfaces
    for y in range(height - 1):
        for x in range(width - 1):
            top_left = y * width + x
            top_right = y * width + (x + 1)
            bottom_left = (y + 1) * width + x
            bottom_right = (y + 1) * width + (x + 1)

            # Top surface triangles
            faces.append([top_left, top_right, bottom_right])
            faces.append([top_left, bottom_right, bottom_left])

            # Base surface triangles
            base_offset = width * height
            faces.append([top_left + base_offset, bottom_left + base_offset, bottom_right + base_offset])
            faces.append([top_left + base_offset, bottom_right + base_offset, top_right + base_offset])

    # Convert to NumPy arrays
    vertices = np.array(vertices)
    faces = np.array(faces)

    # Create mesh
    stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            stl_mesh.vectors[i][j] = vertices[f[j], :]

    # Write to STL file
    stl_mesh.save(stl_path)
    print(f"STL file saved to {stl_path}")

# Example usage
image_to_stl("input_image.png", "output_model.stl", max_height=5, base_thickness=2)
