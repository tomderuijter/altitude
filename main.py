from srtm.base import FileEngine, SRTM3DataLoader

if __name__ == "__main__":
    file_engine = FileEngine(SRTM3DataLoader())
    elevation = file_engine.get_elevation(50.8, 7.5)
    print(elevation)
    print("Program finished.")