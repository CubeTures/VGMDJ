from pathlib import Path

from utils import tag_folder


def main() -> None:
    root = Path("Music")
    album_folders = {f for f in root.rglob("*") if f.is_dir() and f.parent != root}
    for album in album_folders:
        print("Tagging", album.parent.name, f"\t{album.name}")
        tag_folder(album.name, album.parent.name, album)


if __name__ == "__main__":
    main()
