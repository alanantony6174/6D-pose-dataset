import open3d as o3d
import os
import sys

def convert_ply_to_pcd(input_ply_file, output_pcd_file, write_ascii=True):
    """
    Converts a PLY file to a PCD file using Open3D.

    Args:
        input_ply_file (str): Path to the input PLY file.
        output_pcd_file (str): Path to the desired output PCD file.
        write_ascii (bool): If True, writes PCD in ASCII format.
                             If False, writes in binary format (smaller, faster).
    """
    print(f"Attempting to read PLY file: {input_ply_file}")

    # Check if input file exists
    if not os.path.exists(input_ply_file):
        print(f"Error: Input file not found at {input_ply_file}")
        return False

    try:
        # Read the point cloud from the PLY file
        pcd = o3d.io.read_point_cloud(input_ply_file)

        # Check if the point cloud was loaded successfully and has points
        if not pcd.has_points():
            print(f"Error: Could not read points from {input_ply_file}. Is it a valid point cloud PLY?")
            # Check if it might be a mesh file instead
            try:
               mesh = o3d.io.read_triangle_mesh(input_ply_file)
               if mesh.has_vertices():
                  print("Info: Input file seems to be a mesh. Extracting vertices.")
                  pcd = mesh.sample_points_uniformly(number_of_points=len(mesh.vertices)) # Or just use vertices directly
                  # pcd = o3d.geometry.PointCloud() # Alternative: just vertices
                  # pcd.points = mesh.vertices
                  # if mesh.has_vertex_colors():
                  #    pcd.colors = mesh.vertex_colors
                  # if mesh.has_vertex_normals():
                  #    pcd.normals = mesh.vertex_normals # Requires normals calculation if not present
               else:
                  print("Info: Input file read as mesh, but has no vertices.")
                  return False
            except Exception as mesh_e:
               print(f"Info: Could not read as mesh either: {mesh_e}")
               return False # Exit if neither point cloud nor mesh read works


        print(f"Successfully read {len(pcd.points)} points from {input_ply_file}")
        if pcd.has_colors():
            print("Info: Point cloud has color information.")
        if pcd.has_normals():
            print("Info: Point cloud has normal information.")

        # Write the point cloud to the PCD file
        print(f"Writing PCD file to: {output_pcd_file} (ASCII={write_ascii})")
        success = o3d.io.write_point_cloud(output_pcd_file, pcd, write_ascii=write_ascii)

        if success:
            print("Conversion successful!")
            return True
        else:
            print("Error: Failed to write PCD file.")
            return False

    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        return False

# --- Main execution ---
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ply_to_pcd.py <input_ply_file.ply> <output_pcd_file.pcd>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Set write_ascii=False if you prefer binary PCD files
    convert_ply_to_pcd(input_file, output_file, write_ascii=True)