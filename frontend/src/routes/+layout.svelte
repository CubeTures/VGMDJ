<script lang="ts">
	import "./layout.css";
	import favicon from "$lib/assets/favicon.svg";
	import {
		FolderIcon,
		HardDriveDownloadIcon,
		ThumbsDownIcon,
	} from "@lucide/svelte";

	let { children } = $props();
</script>

<svelte:head
	><link
		rel="icon"
		href={favicon}
	/></svelte:head
>
<div class="h-dvh w-dvw flex flex-col">
	<div class="grow overflow-y-scroll bg-mauve-50 relative">{@render children()}</div>
	<div class="bg-mauve-200 flex justify-around p-6">
		<a href="/"><HardDriveDownloadIcon /></a>
		<a href="/boo"><ThumbsDownIcon /></a>
		<a href="/files"><FolderIcon /></a>
	</div>
</div>
