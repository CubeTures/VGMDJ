export interface MediaMetadata {
	path: string;
	title: string | undefined;
	artist: string | undefined;
	track_number: number | undefined;
	disc_number: number | undefined;
	length: number | undefined;
}

export interface FolderMetadata {
	path: string;
	total: number;
	visible: number;
}

export interface Entry {
	name: string;
	isDir: boolean;
	isHidden: boolean;
	metadata: FolderMetadata | MediaMetadata;
}
