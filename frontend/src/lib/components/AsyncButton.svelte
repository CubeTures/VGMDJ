<script lang="ts">
	import { cn } from "$lib/utility";
	import { CheckIcon, Disc3Icon, FrownIcon, SaveIcon } from "@lucide/svelte";
	import type { HTMLAttributes } from "svelte/elements";

	interface Props {
		onclick: () => Promise<boolean>;
		onsuccess?: () => void;
		onfailure?: () => void;
		loading?: boolean;
		success?: boolean | undefined;
		autoResetDelay?: number;
	}

	let {
		onclick,
		onsuccess,
		onfailure,
		loading = $bindable(false),
		success = $bindable(undefined),
		autoResetDelay = 2000,
		...rest
	}: Props & HTMLAttributes<HTMLButtonElement> = $props();

	let resetCallback: number | undefined = undefined;

	async function click() {
		clearTimeout(resetCallback);
		success = undefined;

		loading = true;
		success = await onclick();
		loading = false;

		if (success) {
			onsuccess?.();
		} else {
			onfailure?.();
		}

		resetCallback = setTimeout(() => {
			success = undefined;
		}, autoResetDelay);
	}
</script>

<button
	{...rest}
	class={cn("bg-mauve-200 border border-mauve-400 rounded-full p-2", rest.class)}
	onclick={click}
>
	{#if loading}
		<div class="spinner">
			<Disc3Icon />
		</div>
	{:else if success === undefined}
		<SaveIcon />
	{:else if success === true}
		<CheckIcon />
	{:else if success === false}
		<FrownIcon />
	{/if}
</button>

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
