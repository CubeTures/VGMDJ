<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";
	import AsyncButton from "./AsyncButton.svelte";

	let url = $state("");
	let album = $state("");
	let albumArtist = $state("");
	let quality = $state("mp3");

	async function download() {
		const res = await fetch(`${PUBLIC_API_URL}/download/khinsider`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				url,
				album,
				album_artist: albumArtist,
				quality,
			}),
		});
		return res.ok;
	}
</script>

<div
	class="bg-mauve-200 border border-mauve-400 rounded p-2 flex flex-col gap-2"
>
	<h2 class="font-bold text-lg">KHInsider</h2>
	<div class="grid grid-cols-[auto_1fr] gap-2 items-center">
		<label
			for="url"
			class="text-right">URL</label
		>
		<input
			id="url"
			bind:value={url}
			class="bg-mauve-50 rounded px-1 min-w-0"
		/>

		<label
			for="album"
			class="text-right">Game</label
		>
		<input
			id="album"
			bind:value={album}
			class="bg-mauve-50 rounded px-1 min-w-0"
		/>

		<label
			for="albumArtist"
			class="text-right">Franchise</label
		>
		<input
			id="albumArtist"
			bind:value={albumArtist}
			class="bg-mauve-50 rounded px-1 min-w-0"
		/>

		<label
			for="quality"
			class="text-right">Quality</label
		>
		<input
			id="quality"
			bind:value={quality}
			class="bg-mauve-50 rounded px-1 min-w-0"
		/>
	</div>
	<div class="flex justify-end">
		<AsyncButton onclick={download} />
	</div>
</div>
