<script lang="ts">
	import { cn } from "$lib/utility";
	import { EllipsisVerticalIcon } from "@lucide/svelte";
	import Dialog from "./Dialog.svelte";
	import type { FolderMetadata } from "$lib/types";

	interface Props {
		text: string;
		metadata: FolderMetadata;
		onclick: () => void;
		hidden: boolean;
	}

	const { text, metadata, onclick, hidden }: Props = $props();
	let dialog = $state<HTMLDialogElement>();
</script>

{#snippet Counts()}
	{#if metadata.total > 0}
		{#if metadata.visible == -1}
			<p class="text-nowrap">{metadata.total}</p>
		{:else}
			<p class="text-nowrap">{metadata.visible} / {metadata.total}</p>
		{/if}
	{/if}
{/snippet}

<!-- svelte-ignore a11y_interactive_supports_focus -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class={cn(
		"p-2 border border-mauve-400 rounded text-left bg-mauve-200 flex gap-1",
		hidden ? "bg-mauve-50 border-mauve-50 text-mauve-400" : "",
	)}
	{onclick}
>
	<p class="mr-2 grow text-nowrap truncate min-w-0">{text}</p>
	{@render Counts()}

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
				<p class="font-bold">{text}</p>
				{@render Counts()}
			</div>
		</Dialog>
	</button>
</div>
