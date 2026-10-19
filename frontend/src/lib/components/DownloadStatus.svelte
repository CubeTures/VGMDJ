<script lang="ts">
	import type { DownloadStatusMessage } from "$lib/types";
	import { capitalize } from "$lib/utility";
	import Stream from "./Stream.svelte";

	let messages: Record<string, DownloadStatusMessage> = $state({});

	function onmessage(str: string) {
		const data = JSON.parse(str);
		messages[data.id] = data;
	}

	function progressPercent(track: string): number {
		const [curr, total] = track.split("/");
		return parseInt(curr) / parseInt(total);
	}
</script>

<Stream
	endpoint="/download-status"
	{onmessage}
/>

{#if Object.keys(messages).length > 0}
	{#each Object.keys(messages).toSorted().toReversed() as id (id)}
		{@const message = messages[id]}
		<div class="border bg-mauve-200 border-mauve-400 p-2 gap-2 rounded">
			<div class="flex flex-col">
				<p class="text-lg font-bold">{message.meta.game}</p>
				<p class="text-sm text-mauve-600">{message.meta.franchise}</p>
				<div class="mt-1">
					{#if message.status !== "progress"}
						<p>{capitalize(message.status)}</p>
					{:else}
						{@const prog = message.progress!}
						{@const percent = progressPercent(prog.track)}
						<p class="text-nowrap truncate">
							{prog.filename}
						</p>
						<div
							class="border border-mauve-600 bg-mauve-400 rounded-full h-2 my-0.5"
						>
							<div
								class="bg-mauve-600 h-full"
								style="width: {percent * 100}%"
							></div>
						</div>
						<div class="flex justify-between">
							<p>{prog.track}</p>
							<p>{prog.speed}</p>
						</div>
					{/if}
				</div>
				<p class="text-right text-mauve-600 text-sm">
					{new Date(message.timestamp).toISOString()}
				</p>
			</div>
		</div>
	{/each}
{/if}
