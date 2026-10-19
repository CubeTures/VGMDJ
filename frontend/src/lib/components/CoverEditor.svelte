<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";
	import { cn } from "$lib/utility";
	import { ImageIcon } from "@lucide/svelte";
	import AsyncButton from "./AsyncButton.svelte";

	interface Props {
		dirs: string[];
	}

	const { dirs }: Props = $props();

	const isAlbumArtist = $derived(dirs.length === 1);

	let coverVersion = $state(0);
	const coverUrl = $derived(
		`${PUBLIC_API_URL}/cover?${dirs.map((d) => `dirs=${encodeURIComponent(d)}`).join("&")}&v=${coverVersion}`
	);

	let fileInput: HTMLInputElement | undefined = $state();
	let files: FileList | undefined = $state();
	const file = $derived(files?.[0] ?? null);
	const previewUrl = $derived(file ? URL.createObjectURL(file) : undefined);

	let coverMissing = $state(false);
	let overrideTracks = $state(false);

	async function upload(): Promise<boolean> {
		if (!file) return false;

		const form = new FormData();
		form.append("dirs", JSON.stringify(dirs));
		form.append("image", file);
		if (!isAlbumArtist) {
			form.append("override_tracks", String(overrideTracks));
		}

		const endpoint = isAlbumArtist ? "album_artist" : "album";
		const res = await fetch(`${PUBLIC_API_URL}/cover/${endpoint}`, {
			method: "POST",
			body: form,
		});

		if (res.ok) {
			files = undefined;
			coverMissing = false;
			coverVersion++;
		}
		return res.ok;
	}
</script>

<div class="flex flex-col gap-2">
	<button
		type="button"
		class={cn(
			"size-32 self-center rounded border border-mauve-400 flex items-center justify-center overflow-hidden",
			coverMissing && !file ? "bg-mauve-50 text-mauve-400" : ""
		)}
		onclick={() => fileInput?.click()}
	>
		{#if coverMissing && !file}
			<ImageIcon class="size-10" />
		{:else}
			<img
				src={previewUrl ?? coverUrl}
				alt="Cover art"
				class="size-full object-cover"
				onerror={() => {
					if (!file) coverMissing = true;
				}}
			/>
		{/if}
	</button>
	<input
		bind:this={fileInput}
		bind:files
		type="file"
		accept="image/png,image/jpeg,image/webp"
		class="hidden"
	/>

	{#if !isAlbumArtist}
		<label class="flex items-center gap-2">
			<input
				type="checkbox"
				bind:checked={overrideTracks}
			/>
			Set all track images
		</label>
	{/if}

	<div class="flex justify-end">
		<AsyncButton onclick={upload} />
	</div>
</div>
