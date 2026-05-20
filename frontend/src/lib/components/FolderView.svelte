<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";
	import {
		CheckIcon,
		CornerLeftUpIcon,
		Disc3Icon,
		EyeClosedIcon,
		EyeIcon,
		EyeOffIcon,
		FrownIcon,
		SaveIcon,
	} from "@lucide/svelte";
	import { onMount } from "svelte";
	import { fade } from "svelte/transition";
	import type { Entry, FolderMetadata, MediaMetadata } from "$lib/types";
	import MediaButton from "./MediaButton.svelte";
	import FolderButton from "./FolderButton.svelte";

	const ROOT = "__ROOT_DIR__";

	type Result = "SUCCESS" | "FAILURE" | undefined;

	let dirs: string[] = $state([]);
	let entries: Entry[] = $state([]);
	let loading = $state(false);
	let cache: Record<string, Entry[]> = $state({});
	let hidden: Record<string, boolean> = $state({});
	let result: Result = $state(undefined);
	let showHidden = $state(true);

	function checkCache(dirs: string[]): Entry[] | undefined {
		const key = dirs.length === 0 ? ROOT : dirs.join("/");
		return cache[key];
	}

	function updateCache(dirs: string[], entries: Entry[]) {
		const key = dirs.length === 0 ? ROOT : dirs.join("/");
		cache[key] = entries;
	}

	async function walk(dirs: string[]) {
		const cached = checkCache(dirs);
		if (cached !== undefined) {
			entries = cached;
			return;
		}

		const res = await fetch(`${PUBLIC_API_URL}/walk`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(dirs),
		});
		entries = await res.json();
		updateCache(dirs, entries);
	}

	function open(dir: string) {
		loading = true;
		walk(dirs.concat(dir));
		dirs.push(dir);
		result = undefined;
		hidden = {};
		loading = false;
	}

	function close() {
		loading = true;
		walk(dirs.slice(0, -1));
		dirs.pop();
		result = undefined;
		hidden = {};
		loading = false;
	}

	function hide(file: string) {
		result = undefined;
		const preHidden = entries.find((e) => e.name === file)?.isHidden;

		if (hidden[file]) {
			hidden[file] = false;
		} else {
			if (preHidden && hidden[file] === undefined) {
				hidden[file] = false;
			} else {
				hidden[file] = true;
			}
		}

		if (preHidden === hidden[file]) {
			delete hidden[file];
		}
	}

	async function save() {
		if (result) return;

		loading = true;
		const res = await fetch(`${PUBLIC_API_URL}/hide`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ dirs, hidden }),
		});
		if (res.ok) {
			for (const entry of entries) {
				if (hidden[entry.name] !== undefined) {
					entry.isHidden = hidden[entry.name];
				}
			}
			updateCache(dirs, entries);
			result = "SUCCESS";
		} else {
			result = "FAILURE";
		}
		loading = false;
	}

	function getDiscCount(disc: number): string {
		const [total, visible] = entries
			.filter((e) => (e.metadata as MediaMetadata).disc_number == disc)
			.reduce(
				([total, visible], e) => [
					total + 1,
					visible + (e.isHidden ? 0 : 1),
				],
				[0, 0],
			);
		return `${visible}/${total}`;
	}

	onMount(() => {
		walk([]);
	});
</script>

{#snippet Up(hidden: boolean)}
	{#if dirs.length > 0}
		<button
			class="bg-mauve-200 border border-mauve-400 rounded-full p-2 {hidden
				? 'invisible'
				: ''}"
			onclick={close}
		>
			<CornerLeftUpIcon />
		</button>
	{/if}
{/snippet}

<div class="flex flex-col gap-2 w-full h-full p-2 pb-2 overflow-y-auto">
	<div>
		<h2 class="font-bold text-2xl text-nowrap truncate">
			{dirs.length == 0 ? "Root" : dirs[dirs.length - 1]}
		</h2>
	</div>
	{#each entries as entry}
		{#if entry.isDir}
			<FolderButton
				text={entry.name}
				metadata={entry.metadata as FolderMetadata}
				onclick={() => open(entry.name)}
				hidden={false}
			/>
		{:else}
			{@const meta = entry.metadata as MediaMetadata}
			{#if meta.track_number == 1}
				<div
					class="bg-mauve-400 p-2 -mx-2 px-4 flex justify-between items-center"
				>
					<p class="font-bold text-lg">
						Disc {meta.disc_number}
					</p>
					<p>{getDiscCount(meta.disc_number!)}</p>
				</div>
			{/if}
			{@const _hidden =
				hidden[entry.name] === undefined
					? entry.isHidden
					: hidden[entry.name]}
			{#if showHidden || !entry.isHidden}
				<MediaButton
					metadata={entry.metadata!}
					onclick={() => hide(entry.name)}
					hidden={_hidden}
				/>
			{/if}
		{/if}
	{/each}
	{@render Up(true)}
</div>

<div class="absolute right-2 bottom-2 flex gap-2">
	{#if Object.values(hidden).length > 0}
		<div>
			<button
				class="bg-mauve-200 border border-mauve-400 rounded-full p-2"
				onclick={save}
			>
				{#if result === undefined}
					<SaveIcon />
				{:else if result === "FAILURE"}
					<FrownIcon />
				{:else if result === "SUCCESS"}
					<CheckIcon />
				{/if}
			</button>
		</div>
	{/if}
	<button
		class="bg-mauve-200 border border-mauve-400 rounded-full p-2"
		onclick={() => (showHidden = !showHidden)}
	>
		{#if showHidden}
			<EyeIcon />
		{:else}
			<EyeOffIcon />
		{/if}
	</button>
	{@render Up(false)}
</div>

{#if loading}
	<div
		class="bg-mauve-900/50 absolute inset-0 flex justify-center items-center"
		transition:fade
	>
		<div class="spinner">
			<Disc3Icon class="size-16" />
		</div>
	</div>
{/if}

<style>
	.spinner {
		animation-name: spin;
		animation-duration: 500ms;
		animation-iteration-count: infinite;
		animation-timing-function: linear;
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
</style>
