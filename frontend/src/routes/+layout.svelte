<script lang="ts">
	import "./layout.css";
	import favicon from "$lib/assets/favicon.ico";
	import {
		FolderIcon,
		HardDriveDownloadIcon,
		SettingsIcon,
	} from "@lucide/svelte";
	import { resolve } from "$app/paths";
	import { page } from "$app/state";

	let { children } = $props();

	let path = $derived(page.url.pathname);
</script>

<svelte:head
	><link
		rel="icon"
		href={favicon}
	/></svelte:head
>
<div class="h-dvh w-dvw flex flex-col">
	<div class="grow overflow-y-scroll bg-mauve-50 relative">
		{@render children()}
	</div>
	<div
		class="bg-mauve-200 flex justify-around p-6 border-t border-t-mauve-400"
	>
		<a
			href={resolve("/")}
			class={path == "/" ? "" : "unselected"}><HardDriveDownloadIcon /></a
		>
		<a
			href={resolve("/files")}
			class={path == "/files/" ? "" : "unselected"}><FolderIcon /></a
		>
		<a
			href={resolve("/prefs")}
			class={path == "/prefs/" ? "" : "unselected"}><SettingsIcon /></a
		>
	</div>
</div>

<style>
	.unselected {
		filter: brightness(0) saturate(100%) invert(45%) sepia(6%)
			saturate(1049%) hue-rotate(246deg) brightness(91%) contrast(83%);
	}
</style>
