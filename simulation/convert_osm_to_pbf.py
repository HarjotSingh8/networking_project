import osmium
import sys
import os

def convert_osm_to_pbf(input_file, output_file):
    """
    Converts an OSM file to PBF format.

    Args:
        input_file (str): Path to the input OSM file.
        output_file (str): Path to the output PBF file.
    """
    try:
        # Remove the output file if it already exists
        if os.path.exists(output_file):
            os.remove(output_file)

        writer = osmium.SimpleWriter(output_file)

        class OSMHandler(osmium.SimpleHandler):
            def __init__(self, writer):
                super().__init__()
                self.writer = writer

            def node(self, n):
                self.writer.add_node(n)

            def way(self, w):
                self.writer.add_way(w)

            def relation(self, r):
                self.writer.add_relation(r)

        handler = OSMHandler(writer)
        handler.apply_file(input_file, osmium.osm.osm_entity_bits.ALL)

        writer.close()
        print(f"Conversion successful: {output_file}")
    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_osm_to_pbf.py <input.osm> <output.pbf>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_osm_to_pbf(input_file, output_file)