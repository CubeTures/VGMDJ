<script lang="ts">
	import type { MediaMetadata } from "$lib/types";
	import { cn, lengthToTime } from "$lib/utility";
	import { EllipsisVerticalIcon } from "@lucide/svelte";
	import Dialog from "./Dialog.svelte";

	interface Props {
		metadata: MediaMetadata;
		onclick: () => void;
		hidden: boolean;
	}

	const { metadata, onclick, hidden }: Props = $props();
	let length = $derived(lengthToTime(metadata.length!));
	let dialog = $state<HTMLDialogElement>();
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class={cn(
		"flex gap-1 items-center p-2 border border-mauve-400 rounded text-left bg-mauve-200",
		hidden ? "bg-mauve-50 border-mauve-50 text-mauve-400" : ""
	)}
	{onclick}
>
	<div>
		{metadata.track_number}
	</div>
	<div class="flex flex-col grow min-w-0 mx-2">
		<p class="text-nowrap truncate">{metadata.title}</p>
		<p
			class="text-nowrap truncate text-sm {hidden
				? 'text-mauve-300'
				: 'text-mauve-600'}"
		>
			{metadata.artist}
		</p>
	</div>
	<div>
		{length}
	</div>
	<button
		onclick={(e) => {
			e.stopPropagation();
			dialog?.showModal();
		}}
	>
		<EllipsisVerticalIcon />
		<Dialog bind:dialog>
			<div
				class="bg-mauve-100 border border-mauve-400 p-4 flex flex-col gap-1 rounded text-left max-h-[50dvh] overflow-y-auto"
			>
				<p>
					{metadata.disc_number} - {metadata.track_number}
				</p>
				<p class="font-bold">{metadata.title}</p>
				<p class="text-mauve-600">{metadata.artist}</p>
				<p>{length}</p>
				<code class="text-sm">{metadata.path}</code>
			</div>
		</Dialog>
	</button>
</div>
